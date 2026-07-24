using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Net.Http;
using System.Threading.Tasks;
using System.Xml.Linq;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace NullZoneTool
{
    public partial class MainForm : Form
    {
        private DataStore dataStore;
        private static readonly HttpClient AvatarHttpClient = CreateAvatarHttpClient();
        private readonly Dictionary<string, Image> avatarCache = new(StringComparer.Ordinal);
        private readonly Dictionary<string, string> profileNameCache = new(StringComparer.Ordinal);
        private readonly string avatarCacheDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "NullZone", "AvatarCache");

        public MainForm()
        {
            InitializeComponent();
            ShowIcon = true;
            LoadWindowIcon();
            LoadBranding();
            ConfigureWindowChrome();
            InitializeApp();
        }


        [DllImport("user32.dll")]
        private static extern bool ReleaseCapture();

        [DllImport("user32.dll")]
        private static extern IntPtr SendMessage(IntPtr hWnd, int msg, int wParam, int lParam);


        private void LoadWindowIcon()
        {
            try
            {
                // Uses the icon embedded in NullZone.exe for the window and taskbar.
                var executableIcon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
                if (executableIcon != null)
                    Icon = (Icon)executableIcon.Clone();
            }
            catch
            {
                // The icon is visual only and must never affect application startup.
            }
        }

        private void LoadBranding()
        {
            try
            {
                var assembly = Assembly.GetExecutingAssembly();
                using var stream = assembly.GetManifestResourceStream("NullZoneTool.nz_logo.png");
                if (stream != null)
                    logoBox.Image = System.Drawing.Image.FromStream(stream);
            }
            catch
            {
                // Branding is visual only; the application remains usable if the image cannot load.
            }
        }

        private void ConfigureWindowChrome()
        {
            btnClose.Click += (_, _) => Close();
            btnMinimize.Click += (_, _) => WindowState = FormWindowState.Minimized;
            btnClose.MouseEnter += (_, _) => btnClose.BackColor = System.Drawing.Color.FromArgb(190, 55, 65);
            btnClose.MouseLeave += (_, _) => btnClose.BackColor = Theme.Background;
            btnMinimize.MouseEnter += (_, _) => btnMinimize.BackColor = Theme.SurfaceAlt;
            btnMinimize.MouseLeave += (_, _) => btnMinimize.BackColor = Theme.Background;

            titleBar.MouseDown += DragWindow;
            lblWindowTitle.MouseDown += DragWindow;
            btnDiscord.Click += (_, _) => OpenDiscord();
        }

        private void DragWindow(object? sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left) return;
            ReleaseCapture();
            SendMessage(Handle, 0xA1, 0x2, 0);
        }


        private void OpenDiscord()
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = "https://discord.gg/nullzone",
                UseShellExecute = true
            });
        }

        private static HttpClient CreateAvatarHttpClient()
        {
            var client = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(8)
            };
            client.DefaultRequestHeaders.UserAgent.ParseAdd("NullZoneTool/1.0");
            return client;
        }

        private void AccountsTable_CellPainting(object? sender, DataGridViewCellPaintingEventArgs e)
        {
            if (e.RowIndex < 0 || e.ColumnIndex != 0)
                return;

            e.PaintBackground(e.CellBounds, true);

            string username = e.FormattedValue?.ToString() ?? string.Empty;
            string steamId = accountsTable.Rows[e.RowIndex].Cells[1].Value?.ToString() ?? string.Empty;
            string displayName = profileNameCache.TryGetValue(steamId, out string? publicName)
                && !string.IsNullOrWhiteSpace(publicName)
                ? publicName
                : username;
            var avatarBounds = new Rectangle(e.CellBounds.X + 10, e.CellBounds.Y + 7, 36, 36);

            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            using (var avatarPath = new GraphicsPath())
            {
                avatarPath.AddEllipse(avatarBounds);
                GraphicsState graphicsState = e.Graphics.Save();
                e.Graphics.SetClip(avatarPath);

                if (avatarCache.TryGetValue(steamId, out Image? avatar))
                {
                    e.Graphics.DrawImage(avatar, avatarBounds);
                }
                else
                {
                    using var avatarBrush = new SolidBrush(Color.FromArgb(29, 64, 108));
                    e.Graphics.FillEllipse(avatarBrush, avatarBounds);
                }

                e.Graphics.Restore(graphicsState);
            }

            if (!avatarCache.ContainsKey(steamId))
            {
                string initials = GetInitials(displayName);
                using var initialsFont = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
                TextRenderer.DrawText(
                    e.Graphics, initials, initialsFont,
                    avatarBounds, Theme.Text,
                    TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter | TextFormatFlags.NoPadding);
            }

            using (var avatarBorder = new Pen(Color.FromArgb(42, 82, 132), 1F))
                e.Graphics.DrawEllipse(avatarBorder, avatarBounds);

            var textBounds = new Rectangle(
                e.CellBounds.X + 55, e.CellBounds.Y,
                Math.Max(0, e.CellBounds.Width - 60), e.CellBounds.Height);

            TextRenderer.DrawText(
                e.Graphics, displayName, e.CellStyle.Font ?? accountsTable.Font,
                textBounds, e.CellStyle.ForeColor,
                TextFormatFlags.Left | TextFormatFlags.VerticalCenter |
                TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix);

            using var gridPen = new Pen(accountsTable.GridColor);
            e.Graphics.DrawLine(gridPen, e.CellBounds.Left, e.CellBounds.Bottom - 1, e.CellBounds.Right, e.CellBounds.Bottom - 1);
            e.Handled = true;
        }

        private async Task LoadAvatarAsync(string steamId)
        {
            if (string.IsNullOrWhiteSpace(steamId))
                return;

            bool hasAvatar = avatarCache.ContainsKey(steamId);
            bool hasProfileName = profileNameCache.ContainsKey(steamId);
            if (hasAvatar && hasProfileName)
                return;

            Image? image = null;
            string? profileName = null;

            try
            {
                Directory.CreateDirectory(avatarCacheDirectory);
                string imageCachePath = Path.Combine(avatarCacheDirectory, steamId + ".jpg");
                string nameCachePath = Path.Combine(avatarCacheDirectory, steamId + ".name.txt");

                if (!hasAvatar && File.Exists(imageCachePath))
                {
                    try
                    {
                        byte[] cachedBytes = await File.ReadAllBytesAsync(imageCachePath).ConfigureAwait(false);
                        image = CreateDetachedImage(cachedBytes);
                    }
                    catch
                    {
                        try { File.Delete(imageCachePath); } catch { }
                    }
                }

                if (!hasProfileName && File.Exists(nameCachePath))
                {
                    try
                    {
                        profileName = (await File.ReadAllTextAsync(nameCachePath).ConfigureAwait(false)).Trim();
                        if (string.IsNullOrWhiteSpace(profileName))
                            profileName = null;
                    }
                    catch
                    {
                        try { File.Delete(nameCachePath); } catch { }
                    }
                }

                // Request the public Steam profile only when either piece of visual data is missing.
                if ((!hasAvatar && image == null) || (!hasProfileName && profileName == null))
                {
                    string profileXml = await AvatarHttpClient.GetStringAsync(
                        $"https://steamcommunity.com/profiles/{steamId}?xml=1").ConfigureAwait(false);

                    var document = XDocument.Parse(profileXml);
                    XElement? root = document.Root;

                    if (!hasProfileName && profileName == null)
                    {
                        profileName = root?.Element("steamID")?.Value?.Trim();
                        if (!string.IsNullOrWhiteSpace(profileName))
                        {
                            try { await File.WriteAllTextAsync(nameCachePath, profileName).ConfigureAwait(false); } catch { }
                        }
                    }

                    if (!hasAvatar && image == null)
                    {
                        string? avatarUrl = root?.Element("avatarFull")?.Value?.Trim();
                        if (!string.IsNullOrWhiteSpace(avatarUrl))
                        {
                            byte[] imageBytes = await AvatarHttpClient.GetByteArrayAsync(avatarUrl).ConfigureAwait(false);
                            image = CreateDetachedImage(imageBytes);
                            try { await File.WriteAllBytesAsync(imageCachePath, imageBytes).ConfigureAwait(false); } catch { }
                        }
                    }
                }

                if (IsDisposed || !IsHandleCreated)
                {
                    image?.Dispose();
                    return;
                }

                Image? loadedImage = image;
                string? loadedProfileName = profileName;
                BeginInvoke(new Action(() =>
                {
                    if (loadedImage != null)
                    {
                        if (avatarCache.TryGetValue(steamId, out Image? oldImage))
                            oldImage.Dispose();
                        avatarCache[steamId] = loadedImage;
                    }

                    if (!string.IsNullOrWhiteSpace(loadedProfileName))
                        profileNameCache[steamId] = loadedProfileName;

                    accountsTable.Invalidate();
                }));
            }
            catch
            {
                image?.Dispose();
                // Profile loading is visual only. The stored account name and initials remain as fallback.
            }
        }

        private static Image CreateDetachedImage(byte[] bytes)
        {
            using var stream = new MemoryStream(bytes);
            using var source = Image.FromStream(stream);
            return new Bitmap(source);
        }

        private static string GetInitials(string username)
        {
            var parts = username
                .Split(new[] { ' ', '_', '-', '.' }, StringSplitOptions.RemoveEmptyEntries);

            if (parts.Length >= 2)
                return string.Concat(parts[0][0], parts[1][0]).ToUpperInvariant();

            return username.Length >= 2
                ? username.Substring(0, 2).ToUpperInvariant()
                : username.ToUpperInvariant();
        }

        private void InitializeApp()
        {
            dataStore = new DataStore();
            LoadAccountsFromStorage();
            RefreshStatus();
            AttachEventHandlers();
        }

        private void AttachEventHandlers()
        {
            btnImportToken.Click += BtnImportToken_Click;
            btnResetSteam.Click += BtnResetSteam_Click;
            btnStartSteam.Click += BtnStartSteam_Click;
            btnSaveConfig.Click += BtnSaveConfig_Click;
            btnRestoreConfig.Click += BtnRestoreConfig_Click;
            btnExportAccounts.Click += BtnExportAccounts_Click;
            btnKillSteam.Click += BtnKillSteam_Click;

            accountsTable.DragEnter += AccountsTable_DragEnter;
            accountsTable.DragDrop += AccountsTable_DragDrop;
            accountsTable.MouseDown += AccountsTable_MouseDown;
            accountsTable.KeyDown += AccountsTable_KeyDown;
            accountsTable.CellPainting += AccountsTable_CellPainting;
        }

        private void LoadAccountsFromStorage()
        {
            var accounts = dataStore.GetAllAccounts();
            foreach (var account in accounts)
            {
                AddAccountRow(account.Username, account.SteamId);
            }
        }

        private void RefreshStatus()
        {
            string currentLogin = ConfigHelper.GetCurrentAccount();
            lblStatus.Text = !string.IsNullOrEmpty(currentLogin) 
                ? $"Logged in:\n{currentLogin}" 
                : "Status:\nNot logged in";
        }

        private void AddAccountRow(string username, string steamid)
        {
            int rowIndex = accountsTable.Rows.Add();
            accountsTable.Rows[rowIndex].Cells[0].Value = username;
            accountsTable.Rows[rowIndex].Cells[1].Value = steamid;
            _ = LoadAvatarAsync(steamid);
        }

        private void BtnImportToken_Click(object sender, EventArgs e)
        {
            using (var dialog = new TokenImportDialog())
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    string inputText = dialog.TokenText;
                    if (!string.IsNullOrWhiteSpace(inputText))
                    {
                        string[] lines = inputText.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                        int imported = 0;
                        foreach (string line in lines)
                        {
                            if (ImportAccountFromLine(line))
                                imported++;
                        }
                        
                        if (imported > 0)
                            MessageBox.Show($"Imported {imported} account(s)", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                }
            }
        }

        private void BtnLoadInventory_Click(object sender, EventArgs e)
        {
            RefreshStatus();
        }

        private void BtnResetSteam_Click(object sender, EventArgs e)
        {
            ConfigHelper.ResetSteam();
            RefreshStatus();
        }

        private void BtnStartSteam_Click(object sender, EventArgs e)
        {
            ConfigHelper.StartSteam();
            RefreshStatus();
        }

        private void BtnKillSteam_Click(object sender, EventArgs e)
        {
            ConfigHelper.KillSteam();
            RefreshStatus();
        }

        private void BtnSaveConfig_Click(object sender, EventArgs e)
        {
            ConfigHelper.SaveCurrentAccounts();
            MessageBox.Show("Configuration saved to backup folder", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            RefreshStatus();
        }

        private void BtnRestoreConfig_Click(object sender, EventArgs e)
        {
            ConfigHelper.RestoreSavedAccounts();
            RefreshStatus();
        }

        private void BtnExportAccounts_Click(object sender, EventArgs e)
        {
            if (accountsTable.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select accounts to export", "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            using (SaveFileDialog dialog = new SaveFileDialog())
            {
                dialog.Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*";
                dialog.Title = "Export Accounts";
                dialog.FileName = "accounts.txt";

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        using (StreamWriter writer = new StreamWriter(dialog.FileName, false, System.Text.Encoding.UTF8))
                        {
                            foreach (DataGridViewRow row in accountsTable.SelectedRows)
                            {
                                string username = row.Cells[0].Value?.ToString();
                                if (!string.IsNullOrEmpty(username))
                                {
                                    var account = dataStore.GetAccount(username);
                                    if (account != null)
                                    {
                                        writer.WriteLine($"{account.Username}----{account.Token}");
                                    }
                                }
                            }
                        }
                        MessageBox.Show($"Exported {accountsTable.SelectedRows.Count} account(s)", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Export error: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }

        private void AccountsTable_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effect = DragDropEffects.Copy;
            }
        }

        private void AccountsTable_DragDrop(object sender, DragEventArgs e)
        {
            string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
            foreach (string file in files)
            {
                if (file.EndsWith(".txt", StringComparison.OrdinalIgnoreCase))
                {
                    ImportFromFile(file);
                }
            }
        }

        private void ImportFromFile(string filePath)
        {
            try
            {
                string[] lines = File.ReadAllLines(filePath, System.Text.Encoding.UTF8);
                int imported = 0;
                foreach (string line in lines)
                {
                    if (ImportAccountFromLine(line))
                        imported++;
                }
                
                if (imported > 0)
                    MessageBox.Show($"Imported {imported} account(s) from file", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"File import error: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void AccountsTable_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Control && e.KeyCode == Keys.V)
            {
                PasteFromClipboard();
                e.Handled = true;
            }
        }

        private void PasteFromClipboard()
        {
            try
            {
                string clipboardText = Clipboard.GetText();
                if (string.IsNullOrEmpty(clipboardText))
                    return;

                string[] lines = clipboardText.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                int imported = 0;
                foreach (string line in lines)
                {
                    if (ImportAccountFromLine(line))
                        imported++;
                }
                
                if (imported > 0)
                    MessageBox.Show($"Imported {imported} account(s) from clipboard", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Paste error: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private bool ImportAccountFromLine(string line)
        {
            string[] parts = line.Trim().Split(new[] { "----" }, StringSplitOptions.None);
            if (parts.Length >= 2)
            {
                string username = parts[0].Trim();
                string token = parts[1].Trim();
                string steamid = TokenParser.GetSteamIdFromToken(token);

                if (!string.IsNullOrEmpty(steamid))
                {
                    dataStore.AddAccount(username, token, steamid);
                    AddAccountRow(username, steamid);
                    return true;
                }
            }
            return false;
        }

        private void AccountsTable_MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Right)
            {
                var hit = accountsTable.HitTest(e.X, e.Y);
                if (hit.RowIndex >= 0)
                {
                    if (!accountsTable.Rows[hit.RowIndex].Selected)
                    {
                        accountsTable.ClearSelection();
                        accountsTable.Rows[hit.RowIndex].Selected = true;
                    }

                    ContextMenuStrip contextMenu = new ContextMenuStrip
                    {
                        BackColor = Theme.SurfaceAlt,
                        ForeColor = Theme.Text,
                        ShowImageMargin = false,
                        Renderer = new ToolStripProfessionalRenderer(new NullZoneColorTable())
                    };
                    
                    ToolStripMenuItem loginMenuItem = new ToolStripMenuItem("Login with this account");
                    loginMenuItem.Click += (s, args) => PerformLogin();
                    contextMenu.Items.Add(loginMenuItem);

                    ToolStripMenuItem browserMenuItem = new ToolStripMenuItem("Open profile in browser");
                    browserMenuItem.Click += (s, args) => OpenProfileInBrowser();
                    contextMenu.Items.Add(browserMenuItem);

                    contextMenu.Items.Add(new ToolStripSeparator());

                    ToolStripMenuItem deleteMenuItem = new ToolStripMenuItem("Remove selected");
                    deleteMenuItem.Click += (s, args) => DeleteSelectedAccounts();
                    contextMenu.Items.Add(deleteMenuItem);

                    contextMenu.Show(accountsTable, e.Location);
                }
            }
        }

        private void PerformLogin()
        {
            foreach (DataGridViewRow row in accountsTable.SelectedRows)
            {
                string username = row.Cells[0].Value?.ToString();
                if (!string.IsNullOrEmpty(username))
                {
                    var account = dataStore.GetAccount(username);
                    if (account != null)
                    {
                        ConfigHelper.DoLogin(username, account.Token);
                        break;
                    }
                }
            }
            RefreshStatus();
        }

        private void DeleteSelectedAccounts()
        {
            var rowsToDelete = accountsTable.SelectedRows.Cast<DataGridViewRow>().ToList();
            
            foreach (DataGridViewRow row in rowsToDelete)
            {
                string username = row.Cells[0].Value?.ToString();
                if (!string.IsNullOrEmpty(username))
                {
                    int? accountId = dataStore.GetAccountId(username);
                    if (accountId.HasValue)
                    {
                        dataStore.RemoveAccount(accountId.Value);
                    }
                }
                accountsTable.Rows.Remove(row);
            }
        }

        private void OpenProfileInBrowser()
        {
            foreach (DataGridViewRow row in accountsTable.SelectedRows)
            {
                string steamId = row.Cells[1].Value?.ToString();
                if (!string.IsNullOrEmpty(steamId))
                {
                    string url = $"https://steamcommunity.com/profiles/{steamId}";
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = url,
                        UseShellExecute = true
                    });
                }
            }
        }


        private sealed class NullZoneColorTable : ProfessionalColorTable
        {
            public override System.Drawing.Color MenuItemSelected => System.Drawing.Color.FromArgb(25, 54, 91);
            public override System.Drawing.Color MenuItemBorder => Theme.Accent;
            public override System.Drawing.Color ToolStripDropDownBackground => Theme.SurfaceAlt;
            public override System.Drawing.Color ImageMarginGradientBegin => Theme.SurfaceAlt;
            public override System.Drawing.Color ImageMarginGradientMiddle => Theme.SurfaceAlt;
            public override System.Drawing.Color ImageMarginGradientEnd => Theme.SurfaceAlt;
            public override System.Drawing.Color SeparatorDark => Theme.Border;
            public override System.Drawing.Color SeparatorLight => Theme.Border;
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            foreach (Image image in avatarCache.Values)
                image.Dispose();
            avatarCache.Clear();
            base.OnFormClosing(e);
        }
    }
}

namespace NullZoneTool
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.titleBar = new System.Windows.Forms.Panel();
            this.lblWindowTitle = new System.Windows.Forms.Label();
            this.btnMinimize = new System.Windows.Forms.Button();
            this.btnClose = new System.Windows.Forms.Button();
            this.sidebar = new System.Windows.Forms.Panel();
            this.logoBox = new System.Windows.Forms.PictureBox();
            this.navAccounts = new NullZoneTool.ModernButton();
            this.btnDiscord = new NullZoneTool.ModernButton();
            this.lblVersion = new System.Windows.Forms.Label();
            this.contentPanel = new System.Windows.Forms.Panel();
            this.lblHeading = new System.Windows.Forms.Label();
            this.lblSubheading = new System.Windows.Forms.Label();
            this.accountsCard = new NullZoneTool.RoundedPanel();
            this.lblTableTitle = new System.Windows.Forms.Label();
            this.lblTableHint = new System.Windows.Forms.Label();
            this.tableDivider = new System.Windows.Forms.Panel();
            this.accountsTable = new System.Windows.Forms.DataGridView();
            this.colUsername = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colSteamId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.controlPanel = new NullZoneTool.RoundedPanel();
            this.lblActions = new System.Windows.Forms.Label();
            this.lblActionsHint = new System.Windows.Forms.Label();
            this.btnImportToken = new NullZoneTool.ModernButton();
            this.btnStartSteam = new NullZoneTool.ModernButton();
            this.btnKillSteam = new NullZoneTool.ModernButton();
            this.btnResetSteam = new NullZoneTool.ModernButton();
            this.btnExportAccounts = new NullZoneTool.ModernButton();
            this.btnSaveConfig = new NullZoneTool.ModernButton();
            this.btnRestoreConfig = new NullZoneTool.ModernButton();
            this.statusCard = new NullZoneTool.RoundedPanel();
            this.statusDot = new System.Windows.Forms.Label();
            this.lblStatusTitle = new System.Windows.Forms.Label();
            this.lblStatus = new System.Windows.Forms.Label();
            this.footerLabel = new System.Windows.Forms.Label();
            this.titleBar.SuspendLayout();
            this.sidebar.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.logoBox)).BeginInit();
            this.contentPanel.SuspendLayout();
            this.accountsCard.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.accountsTable)).BeginInit();
            this.controlPanel.SuspendLayout();
            this.statusCard.SuspendLayout();
            this.SuspendLayout();
            // titleBar
            this.titleBar.BackColor = NullZoneTool.Theme.Background;
            this.titleBar.Controls.Add(this.lblWindowTitle);
            this.titleBar.Controls.Add(this.btnMinimize);
            this.titleBar.Controls.Add(this.btnClose);
            this.titleBar.Dock = System.Windows.Forms.DockStyle.Top;
            this.titleBar.Location = new System.Drawing.Point(0, 0);
            this.titleBar.Name = "titleBar";
            this.titleBar.Size = new System.Drawing.Size(940, 36);
            this.titleBar.TabIndex = 0;
            // lblWindowTitle
            this.lblWindowTitle.AutoSize = true;
            this.lblWindowTitle.Font = new System.Drawing.Font("Segoe UI Semibold", 8F, System.Drawing.FontStyle.Bold);
            this.lblWindowTitle.ForeColor = System.Drawing.Color.FromArgb(105, 117, 136);
            this.lblWindowTitle.Location = new System.Drawing.Point(14, 11);
            this.lblWindowTitle.Name = "lblWindowTitle";
            this.lblWindowTitle.Text = "NULLZONE";
            // btnMinimize
            this.btnMinimize.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right;
            this.btnMinimize.BackColor = NullZoneTool.Theme.Background;
            this.btnMinimize.FlatAppearance.BorderSize = 0;
            this.btnMinimize.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnMinimize.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.btnMinimize.ForeColor = NullZoneTool.Theme.Muted;
            this.btnMinimize.Location = new System.Drawing.Point(864, 0);
            this.btnMinimize.Name = "btnMinimize";
            this.btnMinimize.Size = new System.Drawing.Size(38, 36);
            this.btnMinimize.Text = "—";
            this.btnMinimize.UseVisualStyleBackColor = false;
            // btnClose
            this.btnClose.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right;
            this.btnClose.BackColor = NullZoneTool.Theme.Background;
            this.btnClose.FlatAppearance.BorderSize = 0;
            this.btnClose.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnClose.Font = new System.Drawing.Font("Segoe UI Semibold", 14F, System.Drawing.FontStyle.Bold);
            this.btnClose.ForeColor = NullZoneTool.Theme.Muted;
            this.btnClose.Location = new System.Drawing.Point(902, 0);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(38, 36);
            this.btnClose.Text = "×";
            this.btnClose.UseVisualStyleBackColor = false;
            // sidebar
            this.sidebar.BackColor = NullZoneTool.Theme.Sidebar;
            this.sidebar.Controls.Add(this.logoBox);
            this.sidebar.Controls.Add(this.navAccounts);
            this.sidebar.Controls.Add(this.btnDiscord);
            this.sidebar.Dock = System.Windows.Forms.DockStyle.Left;
            this.sidebar.Location = new System.Drawing.Point(0, 36);
            this.sidebar.Name = "sidebar";
            this.sidebar.Size = new System.Drawing.Size(164, 574);
            this.sidebar.TabIndex = 1;
            // logoBox
            this.logoBox.Location = new System.Drawing.Point(14, 15);
            this.logoBox.Name = "logoBox";
            this.logoBox.Size = new System.Drawing.Size(136, 88);
            this.logoBox.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.logoBox.TabStop = false;
            // navAccounts
            this.navAccounts.BorderColor = System.Drawing.Color.FromArgb(43, 78, 130);
            this.navAccounts.BorderThickness = 1;
            this.navAccounts.ForeColor = NullZoneTool.Theme.Text;
            this.navAccounts.Location = new System.Drawing.Point(14, 124);
            this.navAccounts.Name = "navAccounts";
            this.navAccounts.NormalColor = System.Drawing.Color.FromArgb(14, 28, 47);
            this.navAccounts.HoverColor = System.Drawing.Color.FromArgb(18, 36, 59);
            this.navAccounts.PressedColor = System.Drawing.Color.FromArgb(20, 42, 68);
            this.navAccounts.Radius = 9;
            this.navAccounts.Size = new System.Drawing.Size(136, 40);
            this.navAccounts.TabIndex = 0;
            this.navAccounts.Text = "●   ACCOUNTS";
            // btnDiscord
            this.btnDiscord.Anchor = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left;
            this.btnDiscord.BorderColor = NullZoneTool.Theme.Discord;
            this.btnDiscord.BorderThickness = 1;
            this.btnDiscord.Font = new System.Drawing.Font("Segoe UI Semibold", 8.5F, System.Drawing.FontStyle.Bold);
            this.btnDiscord.ForeColor = System.Drawing.Color.White;
            this.btnDiscord.HoverColor = NullZoneTool.Theme.DiscordHover;
            this.btnDiscord.Location = new System.Drawing.Point(14, 503);
            this.btnDiscord.Name = "btnDiscord";
            this.btnDiscord.NormalColor = NullZoneTool.Theme.Discord;
            this.btnDiscord.PressedColor = System.Drawing.Color.FromArgb(70, 83, 218);
            this.btnDiscord.Radius = 9;
            this.btnDiscord.Size = new System.Drawing.Size(136, 40);
            this.btnDiscord.TabIndex = 1;
            this.btnDiscord.Text = "JOIN DISCORD";
            // contentPanel
            this.contentPanel.BackColor = NullZoneTool.Theme.Background;
            this.contentPanel.Controls.Add(this.lblHeading);
            this.contentPanel.Controls.Add(this.lblSubheading);
            this.contentPanel.Controls.Add(this.accountsCard);
            this.contentPanel.Controls.Add(this.controlPanel);
            this.contentPanel.Controls.Add(this.statusCard);
            this.contentPanel.Controls.Add(this.footerLabel);
            this.contentPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.contentPanel.Location = new System.Drawing.Point(164, 36);
            this.contentPanel.Name = "contentPanel";
            this.contentPanel.Size = new System.Drawing.Size(776, 574);
            this.contentPanel.TabIndex = 2;
            // lblHeading
            this.lblHeading.AutoSize = true;
            this.lblHeading.Font = new System.Drawing.Font("Segoe UI Semibold", 17F, System.Drawing.FontStyle.Bold);
            this.lblHeading.ForeColor = NullZoneTool.Theme.Text;
            this.lblHeading.Location = new System.Drawing.Point(24, 17);
            this.lblHeading.Name = "lblHeading";
            this.lblHeading.Text = "Accounts";
            // lblSubheading
            this.lblSubheading.AutoSize = true;
            this.lblSubheading.Font = new System.Drawing.Font("Segoe UI", 8.5F);
            this.lblSubheading.ForeColor = NullZoneTool.Theme.Muted;
            this.lblSubheading.Location = new System.Drawing.Point(26, 51);
            this.lblSubheading.Name = "lblSubheading";
            this.lblSubheading.Text = "Import, manage and launch your saved Steam sessions.";
            // accountsCard
            this.accountsCard.BackColor = NullZoneTool.Theme.Surface;
            this.accountsCard.BorderColor = NullZoneTool.Theme.Border;
            this.accountsCard.Controls.Add(this.lblTableTitle);
            this.accountsCard.Controls.Add(this.lblTableHint);
            this.accountsCard.Controls.Add(this.tableDivider);
            this.accountsCard.Controls.Add(this.accountsTable);
            this.accountsCard.Location = new System.Drawing.Point(24, 82);
            this.accountsCard.Name = "accountsCard";
            this.accountsCard.Radius = 12;
            this.accountsCard.Size = new System.Drawing.Size(492, 444);
            this.accountsCard.TabIndex = 0;
            // lblTableTitle
            this.lblTableTitle.AutoSize = true;
            this.lblTableTitle.Font = new System.Drawing.Font("Segoe UI Semibold", 10F, System.Drawing.FontStyle.Bold);
            this.lblTableTitle.ForeColor = NullZoneTool.Theme.Text;
            this.lblTableTitle.Location = new System.Drawing.Point(17, 14);
            this.lblTableTitle.Name = "lblTableTitle";
            this.lblTableTitle.Text = "Saved accounts";
            // lblTableHint
            this.lblTableHint.AutoSize = true;
            this.lblTableHint.Font = new System.Drawing.Font("Segoe UI", 8F);
            this.lblTableHint.ForeColor = NullZoneTool.Theme.Muted;
            this.lblTableHint.Location = new System.Drawing.Point(17, 37);
            this.lblTableHint.Name = "lblTableHint";
            this.lblTableHint.Text = "Right-click an account for more options";
            // tableDivider
            this.tableDivider.BackColor = NullZoneTool.Theme.Border;
            this.tableDivider.Location = new System.Drawing.Point(0, 64);
            this.tableDivider.Name = "tableDivider";
            this.tableDivider.Size = new System.Drawing.Size(492, 1);
            // accountsTable
            this.accountsTable.AllowDrop = true;
            this.accountsTable.AllowUserToAddRows = false;
            this.accountsTable.AllowUserToDeleteRows = false;
            this.accountsTable.AllowUserToResizeColumns = false;
            this.accountsTable.AllowUserToResizeRows = false;
            this.accountsTable.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill;
            this.accountsTable.BackgroundColor = NullZoneTool.Theme.Surface;
            this.accountsTable.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.accountsTable.CellBorderStyle = System.Windows.Forms.DataGridViewCellBorderStyle.SingleHorizontal;
            this.accountsTable.ColumnHeadersBorderStyle = System.Windows.Forms.DataGridViewHeaderBorderStyle.None;
            this.accountsTable.ColumnHeadersHeight = 36;
            this.accountsTable.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
            this.accountsTable.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] { this.colUsername, this.colSteamId });
            this.accountsTable.EnableHeadersVisualStyles = false;
            this.accountsTable.GridColor = NullZoneTool.Theme.Border;
            this.accountsTable.Location = new System.Drawing.Point(11, 76);
            this.accountsTable.MultiSelect = true;
            this.accountsTable.Name = "accountsTable";
            this.accountsTable.ReadOnly = true;
            this.accountsTable.RowHeadersBorderStyle = System.Windows.Forms.DataGridViewHeaderBorderStyle.None;
            this.accountsTable.RowHeadersVisible = false;
            this.accountsTable.RowHeadersWidth = 4;
            this.accountsTable.RowHeadersWidthSizeMode = System.Windows.Forms.DataGridViewRowHeadersWidthSizeMode.DisableResizing;
            this.accountsTable.RowTemplate.Height = 50;
            this.accountsTable.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.accountsTable.Size = new System.Drawing.Size(470, 356);
            this.accountsTable.TabIndex = 1;
            this.accountsTable.DefaultCellStyle.BackColor = NullZoneTool.Theme.Surface;
            this.accountsTable.DefaultCellStyle.ForeColor = NullZoneTool.Theme.Text;
            this.accountsTable.DefaultCellStyle.SelectionBackColor = System.Drawing.Color.FromArgb(18, 35, 56);
            this.accountsTable.DefaultCellStyle.SelectionForeColor = NullZoneTool.Theme.Text;
            this.accountsTable.DefaultCellStyle.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.accountsTable.DefaultCellStyle.Padding = new System.Windows.Forms.Padding(7, 0, 7, 0);
            this.accountsTable.ColumnHeadersDefaultCellStyle.BackColor = NullZoneTool.Theme.SurfaceAlt;
            this.accountsTable.ColumnHeadersDefaultCellStyle.ForeColor = NullZoneTool.Theme.Muted;
            this.accountsTable.ColumnHeadersDefaultCellStyle.Font = new System.Drawing.Font("Segoe UI Semibold", 8F, System.Drawing.FontStyle.Bold);
            this.accountsTable.RowHeadersDefaultCellStyle.BackColor = NullZoneTool.Theme.Surface;
            this.accountsTable.RowHeadersDefaultCellStyle.SelectionBackColor = System.Drawing.Color.FromArgb(18, 35, 56);
            // columns
            this.colUsername.DefaultCellStyle.Padding = new System.Windows.Forms.Padding(51, 0, 7, 0);
            this.colUsername.FillWeight = 90F;
            this.colUsername.HeaderText = "ACCOUNT";
            this.colUsername.Name = "colUsername";
            this.colUsername.ReadOnly = true;
            this.colSteamId.FillWeight = 110F;
            this.colSteamId.HeaderText = "STEAM ID";
            this.colSteamId.Name = "colSteamId";
            this.colSteamId.ReadOnly = true;
            // controlPanel
            this.controlPanel.BackColor = NullZoneTool.Theme.Surface;
            this.controlPanel.BorderColor = NullZoneTool.Theme.Border;
            this.controlPanel.Controls.Add(this.lblActions);
            this.controlPanel.Controls.Add(this.lblActionsHint);
            this.controlPanel.Controls.Add(this.btnImportToken);
            this.controlPanel.Controls.Add(this.btnStartSteam);
            this.controlPanel.Controls.Add(this.btnKillSteam);
            this.controlPanel.Controls.Add(this.btnResetSteam);
            this.controlPanel.Controls.Add(this.btnExportAccounts);
            this.controlPanel.Controls.Add(this.btnSaveConfig);
            this.controlPanel.Controls.Add(this.btnRestoreConfig);
            this.controlPanel.Location = new System.Drawing.Point(532, 82);
            this.controlPanel.Name = "controlPanel";
            this.controlPanel.Radius = 12;
            this.controlPanel.Size = new System.Drawing.Size(220, 342);
            // lblActions
            this.lblActions.AutoSize = true;
            this.lblActions.Font = new System.Drawing.Font("Segoe UI Semibold", 10F, System.Drawing.FontStyle.Bold);
            this.lblActions.ForeColor = NullZoneTool.Theme.Text;
            this.lblActions.Location = new System.Drawing.Point(15, 14);
            this.lblActions.Name = "lblActions";
            this.lblActions.Text = "Quick actions";
            // lblActionsHint
            this.lblActionsHint.AutoSize = true;
            this.lblActionsHint.Font = new System.Drawing.Font("Segoe UI", 7.5F);
            this.lblActionsHint.ForeColor = NullZoneTool.Theme.Muted;
            this.lblActionsHint.Location = new System.Drawing.Point(15, 36);
            this.lblActionsHint.Name = "lblActionsHint";
            this.lblActionsHint.Text = "Steam and account controls";
            // action buttons
            ConfigureActionButton(this.btnImportToken, "+  Import tokens", 61, 190);
            this.btnImportToken.NormalColor = NullZoneTool.Theme.Accent;
            this.btnImportToken.HoverColor = NullZoneTool.Theme.AccentHover;
            this.btnImportToken.PressedColor = System.Drawing.Color.FromArgb(42, 105, 210);
            this.btnImportToken.BorderColor = NullZoneTool.Theme.Accent;
            ConfigureActionButton(this.btnStartSteam, "Launch Steam", 105, 190);
            ConfigureActionButton(this.btnKillSteam, "Kill Steam", 149, 190);
            this.btnKillSteam.NormalColor = System.Drawing.Color.FromArgb(39, 18, 23);
            this.btnKillSteam.HoverColor = System.Drawing.Color.FromArgb(55, 23, 29);
            this.btnKillSteam.PressedColor = System.Drawing.Color.FromArgb(66, 27, 34);
            this.btnKillSteam.BorderColor = System.Drawing.Color.FromArgb(91, 37, 45);
            this.btnKillSteam.ForeColor = System.Drawing.Color.FromArgb(255, 145, 153);
            ConfigureActionButton(this.btnResetSteam, "Reset Steam", 193, 190);
            ConfigureActionButton(this.btnExportAccounts, "Export selected accounts", 237, 190);
            ConfigureActionButton(this.btnSaveConfig, "Save config", 286, 92);
            ConfigureActionButton(this.btnRestoreConfig, "Restore", 286, 92);
            this.btnRestoreConfig.Location = new System.Drawing.Point(113, 286);
            // statusCard
            this.statusCard.BackColor = NullZoneTool.Theme.Surface;
            this.statusCard.BorderColor = NullZoneTool.Theme.Border;
            this.statusCard.Controls.Add(this.statusDot);
            this.statusCard.Controls.Add(this.lblStatusTitle);
            this.statusCard.Controls.Add(this.lblStatus);
            this.statusCard.Location = new System.Drawing.Point(532, 440);
            this.statusCard.Name = "statusCard";
            this.statusCard.Radius = 12;
            this.statusCard.Size = new System.Drawing.Size(220, 86);
            // statusDot
            this.statusDot.AutoSize = true;
            this.statusDot.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.statusDot.ForeColor = NullZoneTool.Theme.Success;
            this.statusDot.Location = new System.Drawing.Point(14, 13);
            this.statusDot.Name = "statusDot";
            this.statusDot.Text = "●";
            // lblStatusTitle
            this.lblStatusTitle.AutoSize = true;
            this.lblStatusTitle.Font = new System.Drawing.Font("Segoe UI Semibold", 9F, System.Drawing.FontStyle.Bold);
            this.lblStatusTitle.ForeColor = NullZoneTool.Theme.Text;
            this.lblStatusTitle.Location = new System.Drawing.Point(35, 15);
            this.lblStatusTitle.Name = "lblStatusTitle";
            this.lblStatusTitle.Text = "Steam status";
            // lblStatus
            this.lblStatus.Font = new System.Drawing.Font("Segoe UI", 8.25F);
            this.lblStatus.ForeColor = NullZoneTool.Theme.Muted;
            this.lblStatus.Location = new System.Drawing.Point(15, 43);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(190, 36);
            this.lblStatus.Text = "Status: Not logged in";
            // footerLabel
            this.footerLabel.AutoSize = true;
            this.footerLabel.Font = new System.Drawing.Font("Segoe UI", 7.5F);
            this.footerLabel.ForeColor = System.Drawing.Color.FromArgb(72, 83, 99);
            this.footerLabel.Location = new System.Drawing.Point(26, 548);
            this.footerLabel.Name = "footerLabel";
            this.footerLabel.Text = "Tip: drag a .txt file here or press Ctrl+V to import accounts.";
            // MainForm
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = NullZoneTool.Theme.Background;
            this.ClientSize = new System.Drawing.Size(940, 610);
            this.Controls.Add(this.contentPanel);
            this.Controls.Add(this.sidebar);
            this.Controls.Add(this.titleBar);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.MaximizeBox = false;
            this.MinimumSize = new System.Drawing.Size(940, 610);
            this.MaximumSize = new System.Drawing.Size(940, 610);
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "NullZone Account Manager";
            this.titleBar.ResumeLayout(false);
            this.titleBar.PerformLayout();
            this.sidebar.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.logoBox)).EndInit();
            this.contentPanel.ResumeLayout(false);
            this.contentPanel.PerformLayout();
            this.accountsCard.ResumeLayout(false);
            this.accountsCard.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.accountsTable)).EndInit();
            this.controlPanel.ResumeLayout(false);
            this.controlPanel.PerformLayout();
            this.statusCard.ResumeLayout(false);
            this.statusCard.PerformLayout();
            this.ResumeLayout(false);
        }

        private static void ConfigureActionButton(NullZoneTool.ModernButton button, string text, int top, int width)
        {
            button.Location = new System.Drawing.Point(15, top);
            button.Name = "actionButton";
            button.Size = new System.Drawing.Size(width, 35);
            button.Font = new System.Drawing.Font("Segoe UI Semibold", 8.5F, System.Drawing.FontStyle.Bold);
            button.Text = text;
            button.Radius = 8;
            button.BorderColor = NullZoneTool.Theme.Border;
            button.NormalColor = NullZoneTool.Theme.SurfaceAlt;
            button.HoverColor = NullZoneTool.Theme.SurfaceHover;
            button.PressedColor = System.Drawing.Color.FromArgb(26, 32, 42);
        }

        private System.Windows.Forms.Panel titleBar;
        private System.Windows.Forms.Label lblWindowTitle;
        private System.Windows.Forms.Button btnMinimize;
        private System.Windows.Forms.Button btnClose;
        private System.Windows.Forms.Panel sidebar;
        private System.Windows.Forms.PictureBox logoBox;
        private NullZoneTool.ModernButton navAccounts;
        private NullZoneTool.ModernButton btnDiscord;
        private System.Windows.Forms.Label lblVersion;
        private System.Windows.Forms.Panel contentPanel;
        private System.Windows.Forms.Label lblHeading;
        private System.Windows.Forms.Label lblSubheading;
        private NullZoneTool.RoundedPanel accountsCard;
        private System.Windows.Forms.Label lblTableTitle;
        private System.Windows.Forms.Label lblTableHint;
        private System.Windows.Forms.Panel tableDivider;
        private System.Windows.Forms.DataGridView accountsTable;
        private System.Windows.Forms.DataGridViewTextBoxColumn colUsername;
        private System.Windows.Forms.DataGridViewTextBoxColumn colSteamId;
        private NullZoneTool.RoundedPanel controlPanel;
        private System.Windows.Forms.Label lblActions;
        private System.Windows.Forms.Label lblActionsHint;
        private NullZoneTool.ModernButton btnImportToken;
        private NullZoneTool.ModernButton btnResetSteam;
        private NullZoneTool.ModernButton btnStartSteam;
        private NullZoneTool.ModernButton btnKillSteam;
        private NullZoneTool.ModernButton btnExportAccounts;
        private NullZoneTool.ModernButton btnSaveConfig;
        private NullZoneTool.ModernButton btnRestoreConfig;
        private NullZoneTool.RoundedPanel statusCard;
        private System.Windows.Forms.Label statusDot;
        private System.Windows.Forms.Label lblStatusTitle;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Label footerLabel;
    }
}

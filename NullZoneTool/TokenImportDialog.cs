using System;
using System.Drawing;
using System.Windows.Forms;

namespace NullZoneTool
{
    public class TokenImportDialog : Form
    {
        private TextBox tokenTextBox = null!;
        private ModernButton btnOk = null!;
        private ModernButton btnCancel = null!;
        private Label lblInstruction = null!;

        public string TokenText => tokenTextBox.Text;

        public TokenImportDialog()
        {
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            Text = "Import Accounts";
            ClientSize = new Size(520, 370);
            StartPosition = FormStartPosition.CenterParent;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            BackColor = Theme.Background;
            ForeColor = Theme.Text;
            Font = new Font("Segoe UI", 9F);
            ShowIcon = false;

            var title = new Label
            {
                Text = "Import accounts",
                Font = new Font("Segoe UI Semibold", 17F, FontStyle.Bold),
                ForeColor = Theme.Text,
                AutoSize = true,
                Location = new Point(24, 20)
            };

            lblInstruction = new Label
            {
                Text = "Paste one account per line using the existing format:\nusername----token",
                Location = new Point(27, 62),
                Size = new Size(465, 42),
                ForeColor = Theme.Muted
            };

            tokenTextBox = new TextBox
            {
                Location = new Point(27, 112),
                Size = new Size(466, 180),
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                AcceptsReturn = true,
                AcceptsTab = false,
                BackColor = Theme.Surface,
                ForeColor = Theme.Text,
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Consolas", 9.5F)
            };

            btnOk = new ModernButton
            {
                Text = "Import",
                Location = new Point(287, 313),
                Size = new Size(98, 38),
                DialogResult = DialogResult.OK,
                NormalColor = Theme.Accent,
                HoverColor = Theme.AccentHover,
                PressedColor = Color.FromArgb(52, 116, 216),
                BorderColor = Theme.Accent,
                ForeColor = Color.White
            };

            btnCancel = new ModernButton
            {
                Text = "Cancel",
                Location = new Point(395, 313),
                Size = new Size(98, 38),
                DialogResult = DialogResult.Cancel
            };

            Controls.Add(title);
            Controls.Add(lblInstruction);
            Controls.Add(tokenTextBox);
            Controls.Add(btnOk);
            Controls.Add(btnCancel);

            AcceptButton = btnOk;
            CancelButton = btnCancel;
        }
    }
}

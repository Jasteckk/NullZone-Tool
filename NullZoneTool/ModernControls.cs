using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace NullZoneTool
{
    internal static class Theme
    {
        public static readonly Color Background = Color.FromArgb(5, 7, 10);
        public static readonly Color Sidebar = Color.FromArgb(7, 9, 13);
        public static readonly Color Surface = Color.FromArgb(10, 13, 18);
        public static readonly Color SurfaceAlt = Color.FromArgb(14, 18, 24);
        public static readonly Color SurfaceHover = Color.FromArgb(20, 25, 33);
        public static readonly Color Border = Color.FromArgb(29, 35, 45);
        public static readonly Color Accent = Color.FromArgb(58, 130, 246);
        public static readonly Color AccentHover = Color.FromArgb(76, 145, 255);
        public static readonly Color Discord = Color.FromArgb(88, 101, 242);
        public static readonly Color DiscordHover = Color.FromArgb(106, 117, 255);
        public static readonly Color Text = Color.FromArgb(241, 244, 248);
        public static readonly Color Muted = Color.FromArgb(132, 143, 160);
        public static readonly Color Success = Color.FromArgb(61, 214, 128);
        public static readonly Color Danger = Color.FromArgb(239, 81, 94);
    }

    internal static class UiHelpers
    {
        public static GraphicsPath RoundedRect(Rectangle bounds, int radius)
        {
            int safeRadius = Math.Max(1, Math.Min(radius, Math.Min(bounds.Width, bounds.Height) / 2));
            int diameter = safeRadius * 2;
            var path = new GraphicsPath();
            path.AddArc(bounds.X, bounds.Y, diameter, diameter, 180, 90);
            path.AddArc(bounds.Right - diameter, bounds.Y, diameter, diameter, 270, 90);
            path.AddArc(bounds.Right - diameter, bounds.Bottom - diameter, diameter, diameter, 0, 90);
            path.AddArc(bounds.X, bounds.Bottom - diameter, diameter, diameter, 90, 90);
            path.CloseFigure();
            return path;
        }
    }

    internal class RoundedPanel : Panel
    {
        public int Radius { get; set; } = 12;
        public Color BorderColor { get; set; } = Theme.Border;
        public int BorderThickness { get; set; } = 1;

        public RoundedPanel()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw, true);
            BackColor = Theme.Surface;
        }

        protected override void OnPaintBackground(PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            var rect = ClientRectangle;
            rect.Width -= 1;
            rect.Height -= 1;
            using var path = UiHelpers.RoundedRect(rect, Radius);
            using var fill = new SolidBrush(BackColor);
            e.Graphics.FillPath(fill, path);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            var rect = ClientRectangle;
            rect.Width -= 1;
            rect.Height -= 1;
            using var path = UiHelpers.RoundedRect(rect, Radius);
            if (BorderThickness > 0)
            {
                using var pen = new Pen(BorderColor, BorderThickness);
                e.Graphics.DrawPath(pen, path);
            }
            base.OnPaint(e);
        }

        protected override void OnResize(EventArgs eventargs)
        {
            base.OnResize(eventargs);
            if (Width <= 1 || Height <= 1) return;
            using var path = UiHelpers.RoundedRect(ClientRectangle, Radius);
            Region?.Dispose();
            Region = new Region(path);
        }
    }

    internal class ModernButton : Button
    {
        private Color normalColor = Theme.SurfaceAlt;
        private Color hoverColor = Theme.SurfaceHover;
        private Color pressedColor = Color.FromArgb(25, 31, 41);
        private bool hovering;
        private bool pressing;

        public int Radius { get; set; } = 9;
        public Color NormalColor { get => normalColor; set { normalColor = value; Invalidate(); } }
        public Color HoverColor { get => hoverColor; set { hoverColor = value; Invalidate(); } }
        public Color PressedColor { get => pressedColor; set { pressedColor = value; Invalidate(); } }
        public Color BorderColor { get; set; } = Theme.Border;
        public int BorderThickness { get; set; } = 1;

        public ModernButton()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor | ControlStyles.Selectable, true);
            FlatStyle = FlatStyle.Flat;
            FlatAppearance.BorderSize = 0;
            FlatAppearance.MouseOverBackColor = Color.Transparent;
            FlatAppearance.MouseDownBackColor = Color.Transparent;
            UseVisualStyleBackColor = false;
            BackColor = Color.Transparent;
            ForeColor = Theme.Text;
            Font = new Font("Segoe UI", 9F, FontStyle.Regular);
            Cursor = Cursors.Hand;
            TabStop = false;
            CausesValidation = false;
        }

        protected override void OnGotFocus(EventArgs e) { Invalidate(); base.OnGotFocus(e); }
        protected override void OnLostFocus(EventArgs e) { Invalidate(); base.OnLostFocus(e); }
        protected override void OnMouseEnter(EventArgs e) { hovering = true; Invalidate(); base.OnMouseEnter(e); }
        protected override void OnMouseLeave(EventArgs e) { hovering = false; pressing = false; Invalidate(); base.OnMouseLeave(e); }
        protected override void OnMouseDown(MouseEventArgs mevent) { pressing = true; Invalidate(); base.OnMouseDown(mevent); }
        protected override void OnMouseUp(MouseEventArgs mevent) { pressing = false; Invalidate(); base.OnMouseUp(mevent); }

        protected override void OnPaintBackground(PaintEventArgs pevent)
        {
            // Fully custom painted. Suppressing native Button background prevents focus/hover corner artifacts.
        }

        protected override void OnPaint(PaintEventArgs pevent)
        {
            pevent.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            pevent.Graphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
            pevent.Graphics.Clear(Parent?.BackColor ?? Theme.Surface);

            var rect = ClientRectangle;
            rect.Width -= 1;
            rect.Height -= 1;
            Color fillColor = pressing ? PressedColor : hovering ? HoverColor : NormalColor;

            using var path = UiHelpers.RoundedRect(rect, Radius);
            using var brush = new SolidBrush(fillColor);
            pevent.Graphics.FillPath(brush, path);

            if (BorderThickness > 0)
            {
                using var pen = new Pen(BorderColor, BorderThickness);
                pevent.Graphics.DrawPath(pen, path);
            }

            TextRenderer.DrawText(pevent.Graphics, Text, Font, rect, ForeColor,
                TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter |
                TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix | TextFormatFlags.NoPadding);
        }
    }
}

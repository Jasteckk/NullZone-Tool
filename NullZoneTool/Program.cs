using System.Runtime.InteropServices;

namespace NullZoneTool
{
    internal static class Program
    {
        [DllImport("shell32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern int SetCurrentProcessExplicitAppUserModelID(string appID);

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            // Gives Windows a stable identity so the NullZone icon is used in the taskbar.
            SetCurrentProcessExplicitAppUserModelID("NullZone.NullZoneTool");

            ApplicationConfiguration.Initialize();
            Application.Run(new MainForm());
        }
    }
}

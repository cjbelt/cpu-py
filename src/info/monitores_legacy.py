script = """
        $monitors = @(Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorConnectionParams)
        $sizes = @(Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorBasicDisplayParams)
        Add-Type -AssemblyName System.Windows.Forms
        $screens = [System.Windows.Forms.Screen]::AllScreens

        $output = @()
        for ($i=0; $i -lt $monitors.Count; $i++) {
            $m = $monitors[$i]
            $s = $sizes | Where-Object { $_.InstanceName -eq $m.InstanceName }
            $scr = if ($i -lt $screens.Count) { $screens[$i] } else { $screens[0] }

            $output += [PSCustomObject]@{
                Connection = $m.VideoOutputTechnology
                WidthCm = if ($s) { $s.MaxHorizontalImageSize } else { 0 }
                HeightCm = if ($s) { $s.MaxVerticalImageSize } else { 0 }
                Primary = if ($scr) { $scr.Primary } else { $false }
                WidthPx = if ($scr) { $scr.Bounds.Width } else { 0 }
                HeightPx = if ($scr) { $scr.Bounds.Height } else { 0 }
            }
        }
        $output | ConvertTo-Json
        """

comando = ["powershell", "-NoProfile", "-Command", script]
saida = subprocess.run(comando, text=True, capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()

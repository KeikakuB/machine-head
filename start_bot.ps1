$FILE = 'bot.pid'
# Kill the bot if needed
Try
{
    $ID = Get-Content -Path $FILE
    Stop-Process -Id $ID
}
Catch
{
    $_.Exception.Message
}
# Start the bot
$app = Start-Process -passthru -nonewwindow machine_head.exe
# Store its pid in 'bot.pid' file
echo $app.Id > $FILE

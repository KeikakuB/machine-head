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
$app = Start-Process -passthru -nonewwindow python machine-head.py
# Store its pid in 'bot.pid' file
echo $app.Id > $FILE

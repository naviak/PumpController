def parseAnalogSignal(response,channel):
    i = response.find("0"+str(channel))
    if i > 0:
        analogs = response[i:i+7]
        analogs = analogs.split(":")
        return int(analogs[1])
    else:
        return 0.

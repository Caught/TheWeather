#IPK v.3.0
import os
import time
import json
import gettext
import datetime
from enigma import gRGB
from enigma import eTimer
from Screens.Screen import Screen
from Components.Label import Label
from time import strftime, localtime
from Screens.ChoiceBox import ChoiceBox
from enigma import ePicLoad, getDesktop
from Components.MenuList import MenuList
from Components.Language import language
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap, MovingPixmap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Sources.StaticText import StaticText
from Components.Converter.ClockToText import ClockToText
from Components.MultiContent import MultiContentEntryText
from Components.ActionMap import ActionMap, HelpableActionMap
from Tools.Directories import resolveFilename, SCOPE_CONFIG, SCOPE_PLUGINS, SCOPE_LANGUAGE
from enigma import eListboxPythonMultiContent, loadPNG, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER

# add Lululla
PY3 = False
import sys
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen, Request
    import urllib.request as urllib2
    import http.cookiejar as cookielib
else:
    from urllib2 import HTTPError, URLError, urlopen, Request
    import urllib2
    import cookielib
# add Lululla end

version = '3.0'
PluginLanguageDomain = "FileBrowser"
PluginLanguagePath = "Extensions/TheWeather/locale/"
OAWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('OAWeather'))
lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("TheWeather", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/TheWeather/locale/"))

icoonpath = "Images"
backgroundpath = ""
CFG_DIR = "/etc/enigma2/TheWeather"


def _(txt):
    t = gettext.dgettext("TheWeather", txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


weatherData = []
screens = []
_restartTimer = None
_restartTimerConn = None
_restartInProgress = False


def _doIconpackRestart(session):
    main(session)

SavedLokaleWeer = []
lockaaleStad = ""
citynamedisplay = ""

sz_w = getDesktop(0).size().width()
sz_h = getDesktop(0).size().height()

def getLocWeer(iscity=None):
    global weatherData
    inputCity = iscity
    global lockaaleStad, citynamedisplay
    mydata = []

    lockaaleStad = inputCity
    mydata = inputCity
    match = None
    try:
        citynumb = int(mydata.split("-")[1])
        # response = urllib.request.urlopen("http://api.buienradar.nl/data/forecast/1.1/all/" + str(citynumb))
        # antw = response.read()
        # add Lululla edit
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)
        req = urllib2.Request("http://api.buienradar.nl/data/forecast/1.1/all/" + str(citynumb), data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=15)
        antw = handler.read()
        # add Lululla edit end
        weatherData = json.loads(antw)
        citynamedisplay = str(mydata.split("-")[0])
        return True
    except:
        try:
            snewy = inputCity.replace(" ", "%20").split("_")
            countycodenewy = ""
            citynamenewy = snewy[0]
            if len(snewy) >= 2:
                countycodenewy = snewy[1]
            text = mydata.replace(' ', '%20')
            # add Lululla edit
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
            cookie_jar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
            urllib2.install_opener(opener)
            req = urllib2.Request("https://location.buienradar.nl/1.1/location/search?query=" + citynamenewy, data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            antw = handler.read()
            # add Lululla edit end
            # response = urllib2.urlopen("https://location.buienradar.nl/1.1/location/search?query=" + citynamenewy)
            # antw = response.read()
            staddata = json.loads(antw)
            entryselect = 0
            entrselect = 0
            if citynamenewy:
                for ecpts in staddata:
                    countcode = str(ecpts["countrycode"]).lower()
                    if countcode == countycodenewy.lower():
                        entryselect = entrselect
                        break
                    entrselect += 1

            req = urllib2.Request("https://forecast.buienradar.nl/2.0/forecast/" + str(staddata[entryselect]["id"]), data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            antw = handler.read()
            weatherData = json.loads(antw)
            citynamedisplay = staddata[entryselect]["name"] + "  " + staddata[entryselect]["countrycode"]

            return True
        except Exception as e:
            print(e)
            return False


def getLocWeerFor(inputCity):
    
    try:
        citynumb = int(inputCity.split("-")[1])
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)
        req = urllib2.Request("http://api.buienradar.nl/data/forecast/1.1/all/" + str(citynumb), data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=15)
        antw = handler.read()
        data = json.loads(antw)
        naam = str(inputCity.split("-")[0])
        return data, naam
    except:
        try:
            snewy = inputCity.replace(" ", "%20").split("_")
            countycodenewy = ""
            citynamenewy = snewy[0]
            if len(snewy) >= 2:
                countycodenewy = snewy[1]
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
            cookie_jar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
            urllib2.install_opener(opener)
            req = urllib2.Request("https://location.buienradar.nl/1.1/location/search?query=" + citynamenewy.replace(" ", "%20"), data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            antw = handler.read()
            staddata = json.loads(antw)
            entryselect = 0
            entrselect = 0
            if citynamenewy:
                for ecpts in staddata:
                    countcode = str(ecpts["countrycode"]).lower()
                    if countcode == countycodenewy.lower():
                        entryselect = entrselect
                        break
                    entrselect += 1
            req = urllib2.Request("https://forecast.buienradar.nl/2.0/forecast/" + str(staddata[entryselect]["id"]), data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            antw = handler.read()
            data = json.loads(antw)
            naam = staddata[entryselect]["name"] + "  " + staddata[entryselect]["countrycode"]
            return data, naam
        except Exception as e:
            print("getLocWeerFor fout:", e)
            return None, None


def icontotext(icon):
    text = ""
    if icon == "a":
        text = _("Sunny / Clear")
    elif icon == "aa":
        text = _("Clear night")
    elif icon == "b":
        text = _("Sunny few clouds")
    elif icon == "bb":
        text = _("Light cloudy")
    elif icon == "c":
        text = _("Heavy clouds")
    elif icon == "cc":
        text = _("Heavy clouds")
    elif icon == "d":
        text = _("Changeable and chance of mist")
    elif icon == "dd":
        text = _("Changeable and chance of mist")
    elif icon == "f":
        text = _("Sunny and chance of showers")
    elif icon == "ff":
        text = _("Cloudy and chance of showers")
    elif icon == "g":
        text = _("Sunny and chance of thundershowers")
    elif icon == "gg":
        text = _("Showers and chance of thunder")
    elif icon == "j":
        text = _("Mostly sunny")
    elif icon == "jj":
        text = _("Mostly clear")
    elif icon == "m":
        text = _("Heavy clouds showers possible")
    elif icon == "mm":
        text = _("Heavy clouds showers possible")
    elif icon == "n":
        text = _("Sunny and chance of mist")
    elif icon == "nn":
        text = _("Clear and chance of mist")
    elif icon == "q":
        text = _("Heavy clouds  heavy showers")
    elif icon == "qq":
        text = _("Heavy clouds  heavy showers")
    elif icon == "r":
        text = _("Cloudy")
    elif icon == "rr":
        text = _("Cloudy")
    elif icon == "s":
        text = _("Heavy clouds  thundershowers")
    elif icon == "ss":
        text = _("Heavy clouds  thundershowers")
    elif icon == "t":
        text = _("Heavy clouds and heavy snowfall")
    elif icon == "tt":
        text = _("Heavy clouds and heavy snowfall")
    elif icon == "u":
        text = _("Changeable cloudy light snowfall")
    elif icon == "uu":
        text = _("Changeable cloudy light snowfall")
    elif icon == "v":
        text = _("Heavy clouds light snowfall")
    elif icon == "vv":
        text = _("Heavy clouds light snowfall")
    elif icon == "w":
        text = _("Heavy clouds winter rainfall")
    elif icon == "ww":
        text = _("Heavy clouds winter rainfall")
    else:
        text = _("No info")
    return text


def winddirtext(dirtext):
    text = ""
    if dirtext == "N":
        text = _("N")
    elif dirtext == "NO":
        text = _("NE")
    elif dirtext == "O":
        text = _("E")
    elif dirtext == "ZO":
        text = _("SE")
    elif dirtext == "Z":
        text = _("S")
    elif dirtext == "ZW":
        text = _("SW")
    elif dirtext == "W":
        text = _("W")
    elif dirtext == "NW":
        text = _("NW")
    return text


def kmh_to_beaufort(kmh):
    
    try:
        kmh = float(kmh)
    except (TypeError, ValueError):
        return None
    thresholds = [1, 6, 12, 20, 29, 39, 50, 62, 75, 89, 103, 118]
    for bft, upper in enumerate(thresholds):
        if kmh < upper:
            return bft
    return 12


def windspeed_with_beaufort(kmh):
    
    bft = kmh_to_beaufort(kmh)
    if bft is None:
        return str(kmh) + " km/h"
    return "%s km/h (Bft %s)" % (kmh, bft)


def localWeatherAlert(dayData):
    
    if not dayData:
        return "", ""

    try:
        windkmh = float(dayData.get("windspeed", 0) or 0)
    except (TypeError, ValueError):
        windkmh = 0
    try:
        rainmm = float(dayData.get("precipitationmm", 0) or 0)
    except (TypeError, ValueError):
        rainmm = 0
    try:
        feeltemp = float(dayData.get("feeltemperature", dayData.get("maxtemperature", 0)) or 0)
    except (TypeError, ValueError):
        feeltemp = 0

    bft = kmh_to_beaufort(windkmh)
    kandidaten = []  

    # Wind: from Bft 7 (near gale)
    if bft is not None and bft >= 9:
        kandidaten.append((3, "red", _("Heavy storm!")))
    elif bft is not None and bft >= 7:
        kandidaten.append((2, "orange", _("Strong wind!")))

    # Precipitation
    if rainmm >= 30:
        kandidaten.append((3, "red", _("Very heavy rain!")))
    elif rainmm >= 15:
        kandidaten.append((2, "orange", _("Heavy rain!")))

    # Heat (yellow/orange/red)
    if feeltemp >= 35:
        kandidaten.append((3, "red", _("Extreme heat!")))
    elif feeltemp >= 30:
        kandidaten.append((2, "orange", _("Warm weather!")))

    # Cold (blue, separate scale independent of the red/orange/yellow chain)
    if feeltemp <= -15:
        kandidaten.append((3, "blue", _("Extreme cold!")))
    elif feeltemp <= -8:
        kandidaten.append((2, "blue", _("Severe cold!")))

    if not kandidaten:
        return "", ""

    # Highest priority wins; in case of equal priority: red > orange > blue > yellow
    kleur_volgorde = {"red": 3, "orange": 2, "blue": 1, "yellow": 0}
    kandidaten.sort(key=lambda k: (k[0], kleur_volgorde.get(k[1], 0)), reverse=True)
    _prio, kleur, tekst = kandidaten[0]
    return kleur, tekst


def checkInternet():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    else:
        return True


class sevendays(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        AddNewScreen(self)
        self.onClose.append(lambda: RemoveScreen(self))
        dayinfoblok = ""
        global weatherData
        dataDagen = weatherData["days"]
        self.selected = 0
        self.hourStep = 1
        protemp = []
        peocpic = ""
        try:
            for procdays in dataDagen:
                for prochours in procdays["hours"]:
                    protemp.append(round(prochours["temperature"]))
                if len(protemp) > 3:
                    break
        except:
            pass
        if protemp[0] > protemp[1]:
            peocpic = "tempcold.png"
        elif protemp[0] < protemp[1]:
            peocpic = "temphot.png"
        else:
            peocpic = "tempeven.png"
        peocpichd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/%s" position="1112,143" size="90,80" zPosition="2" transparent="0" alphatest="blend"/>""" % (peocpic)
        peocpicsd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/%s" position="752,99" size="60,53" zPosition="2" transparent="0" alphatest="on"/>""" % (peocpic)
        if sz_w > 1800:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day + 1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                sunrise = "na"
                sunset = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                    sunrise = (str(dataDagen[0]["sunrise"]).split("T")[1])[:-3]
                    sunset = (str(dataDagen[0]["sunset"]).split("T")[1])[:-3]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dagenbefore = dataDagen[day]
                curtemp = int(dagenbefore["maxtemperature"])
                tempdiff = (int(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*31
                yposline = (1200-(curtemp*31))-lineheight
                curtemp = int(dagenbefore["mintemperature"])
                tempdiff = (int(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*31
                yposline = (1200-(curtemp*31))-lineheight
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="636,102" size="150,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconbighd/""" + str(dataUrr) + """.png" zPosition="3" alphatest="blend"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="1170,343" size="42,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/""" + str(windkracht) + """.png" zPosition="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconhd/""" + str(losticon) + """.png" position=\"""" + str(131 + (248 * day)) + """,498" size="72,72" zPosition="3" transparent="0" alphatest="blend"/>
                    <widget render="Label" source="smallday2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,461" size="135,40" zPosition="3" valign="center" halign="left" font="Regular;34" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="maxtemp2""" + str(day) + """" position=\"""" + str(130 + (248 * day)) + """,571" size="90,54" zPosition="3" font="Regular;48" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
                    <widget render="Label" source="minitemp2""" + str(day) + """" position=\"""" + str(240 + (248 * day)) + """,587" size="90,36" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="weertype2""" + str(day) + """" position=\"""" + str(99 + (248 * day)) + """,617" size="220,86" zPosition="3" valign="center" halign="center" font="Regular;24" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="sunriselab" position="625,362" size="200,40" zPosition="3" font="Regular;28" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconhd/sunupdownhd.png" zPosition="3" position="650,295" size="120,60" alphatest="blend"/>"""
                dataUrr = dataDagen[day]["hours"]
                self["bigWeerIcon1" + str(day)] = Pixmap()
                self["bigDirIcon1" + str(day)] = Pixmap()
                self["smallday2" + str(day)] = StaticText()
                self["maxtemp2" + str(day)] = StaticText()
                self["minitemp2" + str(day)] = StaticText()
                self["weertype2" + str(day)] = StaticText()
                self["sunriselab" + str(day)] = StaticText()
                for slotIdx in range(0, min(8, len(dataUrr))):
                    data = dataUrr[slotIdx]
                    dayinfoblok += """<widget name="dayIcon""" + str(day) + "" + str(uurcount) + """" position=\"""" + str(120 + (216 * uurcount)) + """,749" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="blend"/>"""
                    uurcount += 1
                    self["dayIcon" + str(day) + str(uurcount)] = Pixmap()

            for uur in range(0, 8):
                slotNr = uur
                dayinfoblok += """<widget name="vlakuur""" + str(slotNr) + """" position=\"""" + str(98 + (216 * slotNr)) + """,736" size="191,305" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/patches/vlak_uur""" + str(slotNr) + """.png" zPosition="0" alphatest="blend"/>"""
                dayinfoblok += """
                    <widget render="Label" source="dayhour3""" + str(uur) + """" position=\"""" + str(225 + (216 * uur)) + """,757" size="65,42" zPosition="3" valign="center" halign="left" font="Regular;33" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="daytemp3""" + str(uur) + """" position=\"""" + str(120 + (216 * uur)) + """,820" size="180,54" zPosition="3" valign="center" halign="left" font="Regular;48" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="sunpercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,883" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="daypercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,922" size="120,30" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="hrdayper3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,961" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="dayspeed3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,1000" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="sunicon""" + str(uur) + """" position=\"""" + str(114 + (216 * uur)) + """,879" size="36,36" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/sunpchd.png" alphatest="blend"/>
                    <widget name="rainicon""" + str(uur) + """" position=\"""" + str(116 + (216 * uur)) + """,921" size="30,30" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/rainhd.png" alphatest="blend"/>
                    <widget name="rhicon""" + str(uur) + """" position=\"""" + str(120 + (216 * uur)) + """,960" size="23,30" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/rhhd.png" alphatest="blend"/>
                    <widget name="windicon""" + str(uur) + """" position=\"""" + str(119 + (216 * uur)) + """,997" size="38,38" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/turbinehd.png" alphatest="blend"/>"""
                self["vlakuur" + str(uur)] = Pixmap()
                self["sunicon" + str(uur)] = Pixmap()
                self["rainicon" + str(uur)] = Pixmap()
                self["rhicon" + str(uur)] = Pixmap()
                self["windicon" + str(uur)] = Pixmap()
                self["dayhour3" + str(uur)] = StaticText()
                self["daytemp3" + str(uur)] = StaticText()
                self["sunpercent3" + str(uur)] = StaticText()
                self["daypercent3" + str(uur)] = StaticText()
                self["hrdayper3" + str(uur)] = StaticText()
                self["dayspeed3" + str(uur)] = StaticText()
            skin = """
                    <screen name="sevenday" title="seven" flags="wfNoBorder" position="center,center" size="1920,1080">
                    <widget name="bgpic" position="0,0" size="1920,1080" zPosition="-1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/backgroundhd.png" position="center,center" size="1920,1080" zPosition="0" alphatest="blend"/>
                    <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1409,72" size="450,35" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget name="yellowdot" position="275,463" size="36,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yeldothd.png" zPosition="3" alphatest="blend"/>
                    <widget render="Label" source="city1" position="608,44" size="705,64" zPosition="3" valign="center" halign="center" font="Regular;48" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="bigtemp1" position="870,122" size="353,118" zPosition="3" valign="center" halign="left" font="Regular;108" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="bigweathertype1" position="870,298" size="480,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="GevoelsTemp1" position="870,250" size="354,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="winddir1" position="870,346" size="345,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="weatheralertbg1" position="1322,240" size="588,72" zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/alert/vlak_alert.png" alphatest="on"/>
                    <widget name="weatheralerticon1" position="1332,244" size="64,64" zPosition="4" alphatest="blend" transparent="1"/>
                    <widget name="weatheralert1" position="1440,244" size="576,64" zPosition="3" valign="center" halign="left" font="Regular;48" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-2,-2"/>""" + peocpichd + dayinfoblok + """
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/bluebutton.png" position="1604,46" size="90,54" zPosition="3" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/menubutton.png" position="1423,46" size="90,54" zPosition="3" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/okbutton.png" position="1531,46" size="54,54" zPosition="3" alphatest="blend"/>
                    </screen>"""
        else:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day + 1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                sunrise = "na"
                sunset = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                    sunrise = (str(dataDagen[0]["sunrise"]).split("T")[1])[:-3]
                    sunset = (str(dataDagen[0]["sunset"]).split("T")[1])[:-3]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dagenbefore = dataDagen[day]
                curtemp = int(dagenbefore["maxtemperature"])
                tempdiff = (int(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*31
                yposline = (1200-(curtemp*31))-lineheight
                curtemp = int(dagenbefore["mintemperature"])
                tempdiff = (int(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*31
                yposline = (1200-(curtemp*31))-lineheight
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="422,76" size="100,100" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconbigsd/""" + str(dataUrr) + """.png" zPosition="3" alphatest="blend"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="778,234" size="28,28" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/""" + str(windkracht) + """.png" zPosition="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/icon/""" + str(losticon) + """.png" position=\"""" + str(87 + (165 * day)) + """,334" size="48,48" zPosition="3" transparent="0" alphatest="blend"/>
                    <widget render="Label" source="smallday2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,308" size="90,24" zPosition="3" valign="center" halign="left" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="maxtemp2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,382" size="60,36" zPosition="3" font="Regular;32" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
                    <widget render="Label" source="minitemp2""" + str(day) + """" position=\"""" + str(160 + (165 * day)) + """,395" size="32,22" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="weertype2""" + str(day) + """" position=\"""" + str(69 + (165 * day)) + """,416" size="138,44" zPosition="3" valign="center" halign="center" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="sunriselab" position="416,248" size="200,40" zPosition="3" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/icon/sunupdownsd.png" zPosition="3" position="426,206" size="80,40" alphatest="blend"/>"""
                dataUrr = dataDagen[day]["hours"]
                self["bigWeerIcon1" + str(day)] = Pixmap()
                self["bigDirIcon1" + str(day)] = Pixmap()
                self["smallday2" + str(day)] = StaticText()
                self["maxtemp2" + str(day)] = StaticText()
                self["minitemp2" + str(day)] = StaticText()
                self["weertype2" + str(day)] = StaticText()
                self["sunriselab" + str(day)] = StaticText()
                for slotIdx in range(0, min(8, len(dataUrr))):
                    data = dataUrr[slotIdx]
                    dayinfoblok += """<widget name="dayIcon""" + str(day) + "" + str(uurcount) + """" position=\"""" + str(80 + (144 * uurcount)) + """,494" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="blend"/>"""
                    uurcount += 1
                    self["dayIcon" + str(day) + str(uurcount)] = Pixmap()

            for uur in range(0, 8):
                slotNr = uur
                dayinfoblok += """<widget name="vlakuur""" + str(slotNr) + """" position=\"""" + str(64 + (144 * slotNr)) + """,489" size="129,205" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/patches/vlak_uursd""" + str(slotNr) + """.png" zPosition="0" alphatest="blend"/>"""
                dayinfoblok += """
                    <widget render="Label" source="dayhour3""" + str(uur) + """" position=\"""" + str(146 + (144 * uur)) + """,506" size="42,28" zPosition="3" valign="center" halign="left" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="daytemp3""" + str(uur) + """" position=\"""" + str(80 + (144 * uur)) + """,540" size="120,36" zPosition="3" valign="center" halign="left" font="Regular;32" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="sunpercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,580" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="daypercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,606" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="hrdayper3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """ ,632" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="dayspeed3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,658" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="sunicon""" + str(uur) + """" position=\"""" + str(76 + (144 * uur)) + """,578" size="24,24" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/sunpcsd.png" alphatest="blend"/>
                    <widget name="rainicon""" + str(uur) + """" position=\"""" + str(77 + (144 * uur)) + """,605" size="20,20" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/rainsd.png" alphatest="blend"/>
                    <widget name="rhicon""" + str(uur) + """" position=\"""" + str(79 + (144 * uur)) + """,632" size="16,20" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/rhsd.png" alphatest="blend"/>
                    <widget name="windicon""" + str(uur) + """" position=\"""" + str(79 + (144 * uur)) + """,656" size="25,25" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/wind/turbine.png" alphatest="blend"/>"""
                self["vlakuur" + str(uur)] = Pixmap()
                self["sunicon" + str(uur)] = Pixmap()
                self["rainicon" + str(uur)] = Pixmap()
                self["rhicon" + str(uur)] = Pixmap()
                self["windicon" + str(uur)] = Pixmap()
                self["dayhour3" + str(uur)] = StaticText()
                self["daytemp3" + str(uur)] = StaticText()
                self["sunpercent3" + str(uur)] = StaticText()
                self["daypercent3" + str(uur)] = StaticText()
                self["hrdayper3" + str(uur)] = StaticText()
                self["dayspeed3" + str(uur)] = StaticText()
            skin = """
                    <screen name="sevenday" title="seven" flags="wfNoBorder" position="center,center" size="1280,720">
                    <widget name="bgpic" position="0,0" size="1280,720" zPosition="-1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/background.png" position="center,center" size="1280,720" zPosition="0" alphatest="blend"/>
                    <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget name="yellowdot" position="184,307" size="24,24" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yeldot.png" zPosition="3" alphatest="blend"/>
                    <widget render="Label" source="city1" position="405,37" size="470,42" zPosition="3" valign="center" halign="center" font="Regular;32" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="bigtemp1" position="565,88" size="235,76" zPosition="3" valign="center" halign="left" font="Regular;72" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="bigweathertype1" position="565,208" size="320,30" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="GevoelsTemp1" position="565,176" size="236,30" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="winddir1" position="565,240" size="230,30" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="weatheralertbg1"   position="877,162"  size="398,48"  zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/alert/vlak_alertsd.png" alphatest="on"/>
                    <widget name="weatheralerticon1" position="883,165"  size="42,42"   zPosition="4" alphatest="blend" transparent="1"/>
                    <widget name="weatheralert1"     position="955,165"  size="340,42"  zPosition="3" valign="center" halign="left" font="Regular;32" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-2,-2"/>""" + peocpicsd + dayinfoblok + """
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/bluebuttonsd.png" position="1070,29" size="60,36" zPosition="3" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/menubuttonsd.png" position="949,29" size="60,36" zPosition="3" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/okbuttonsd.png" position="1021,29" size="36,36" zPosition="3" alphatest="blend"/>
                    </screen>"""

        self["city1"] = StaticText()
        self["city1"].text = str(citynamedisplay)
        self["bigtemp1"] = StaticText()
        self["bigweathertype1"] = StaticText()
        self["GevoelsTemp1"] = StaticText()
        self["winddir1"] = StaticText()
        self["weatheralertbg1"] = Pixmap()
        self["weatheralerticon1"] = Pixmap()
        self["weatheralert1"] = Label("")
        self["yellowdot"] = MovingPixmap()
        self["bgpic"] = Pixmap()
        try:
            self.picload = ePicLoad()
            self._picload_conn = safeSignalConnect(self.picload.PictureData, self.bgPictureLoaded)
            self.loadBackground()
        except Exception as e:
            print("TheWeather: ePicLoad niet beschikbaar, standaard achtergrond:", e)
            self.picload = None
        for uur in range(0, 8):
            self["dayhour3" + str(uur)] = StaticText()
            self["dayhour3" + str(uur)].text = "00h"
            self["daytemp3" + str(uur)] = StaticText()
            self["daytemp3" + str(uur)].text = "--\xb0C"
            self["sunpercent3" + str(uur)] = StaticText()
            self["sunpercent3" + str(uur)].text = "--%"
            self["daypercent3" + str(uur)] = StaticText()
            self["daypercent3" + str(uur)].text = "--%"
            self["hrdayper3" + str(uur)] = StaticText()
            self["hrdayper3" + str(uur)].text = "--%"
            self["dayspeed3" + str(uur)] = StaticText()
            self["dayspeed3" + str(uur)].text = "--Km/h"
            for day in range(0, 7):
                self["dayIcon" + str(day) + str(uur)] = Pixmap()
                self["dayIcon" + str(day) + str(uur)].hide()
        dataDagen = weatherData["days"]
        for day in range(1, 8):
            dagen = dataDagen[day-1]
            hasData = bool(dagen) and (dagen.get("iconcode") or dagen.get("maxtemperature") or dagen.get("mintemperature"))

            self["smallday2" + str(day-1)] = StaticText()
            self["maxtemp2" + str(day-1)] = StaticText()
            self["minitemp2" + str(day-1)] = StaticText()
            self["weertype2" + str(day-1)] = StaticText()

            if not hasData:
                self["smallday2" + str(day-1)].text = ""
                self["maxtemp2" + str(day-1)].text = ""
                self["minitemp2" + str(day-1)].text = ""
                self["weertype2" + str(day-1)].text = ""
                self["bigWeerIcon1" + str(day-1)].hide()
                self["bigDirIcon1" + str(day-1)].hide()
            else:
                self["bigWeerIcon1" + str(day-1)].show()
                self["bigDirIcon1" + str(day-1)].show()

                iconclass = "na"
                if dagen.get("iconcode"):
                    iconclass = dagen["iconcode"]
                info1 = ""
                info2 = ""
                info3 = ""
                if dagen.get("date"):
                    dagen1 = dataDagen[day]
                    mydate = dagen1["date"][:-9]
                    unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
                    unixtimecode = unixtimecode-(86400)
                    info1 += _(str(strftime("%A", localtime(unixtimecode))).title()[:2])
                    info1 += str(strftime(" %d", localtime(unixtimecode)))
                if dagen.get("mintemp"):
                    info2 += '{:>3}'.format(str("%.0f" % dagen["mintemp"]) + "\xb0")
                elif dagen.get("mintemperature"):
                    info2 += '{:>3}'.format(str("%.0f" % dagen["mintemperature"]) + "\xb0")
                if dagen.get("maxtemp"):
                    info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemp"]) + "\xb0")
                elif dagen.get("maxtemperature"):
                    info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemperature"]) + "\xb0")

                self["smallday2" + str(day-1)].text = info1
                self["maxtemp2" + str(day-1)].text = info3
                self["minitemp2" + str(day-1)].text = info2
                self["weertype2" + str(day-1)].text = icontotext(iconclass)

            self["sunriselab"] = StaticText()
            self["sunriselab"].text = sunrise+" - "+sunset
            self["myActionMap"] = ActionMap(["SetupActions", "MenuActions", "ColorActions"], {"menu": self.KeyMenu, "left": self.left, "right": self.right, "cancel": self.cancel, "red": self.cancel, "ok": self.fourteendays, "green": self.toggleHourStep, "yellow": self.openBackgroundPicker, "blue": self.openTwoLocations}, -1)
            self.skin = skin
            self.updateFrameselect()
                
        self.alertFixTimer = eTimer()
        self._alertFixTimer_conn = safeTimerCallback(self.alertFixTimer, self.updateFrameselect)
        self.alertFixTimer.start(200, True)

    def getSlotHours(self, day):
        global weatherData
        dataDagen = weatherData["days"]
        dataUrr = dataDagen[day]["hours"]
        result = []
        datacount = 0
        for data in dataUrr:
            if data.get("hour") is not None and ((data["hour"]-1) % self.hourStep) == 0:
                if datacount < 8:
                    result.append(data)
                    datacount += 1
        return result

    def toggleHourStep(self):
        if self.hourStep == 1:
            self.hourStep = 2
        elif self.hourStep == 2:
            self.hourStep = 3
        else:
            self.hourStep = 1
        self.updateFrameselect()

    def updateFrameselect(self):
        if self.selected < 0:
            self.selected = 6
        elif self.selected > 6:
            self.selected = 0

        if sz_w > 1800:
            self["yellowdot"].moveTo(275 + (248 * self.selected), 463, 2)
        else:
            self["yellowdot"].moveTo(184 + (165 * self.selected), 307, 2)
        self["yellowdot"].startMoving()
        global weatherData
        dataDagen = weatherData["days"]

        temptext = "na"
        if dataDagen[self.selected+0].get("temperature"):
            temptext = dataDagen[self.selected+0]["temperature"]
        dataPerUur = weatherData["days"][0]["hours"]
        self["bigtemp1"].setText("")
        self["bigweathertype1"].setText("")
        self["GevoelsTemp1"].setText("")
        self["winddir1"].setText("")
        try:
            self["bigtemp1"].setText('{:>4}'.format(str("%.1f" % dataPerUur[(0)]["temperature"])))
            self["GevoelsTemp1"].setText(_("Feels Like: ") + str("%.1f" % dataPerUur[(0)]["feeltemperature"]) + "\xb0C")
            self["winddir1"].setText(_("Wind direction: ") + str(winddirtext(dataPerUur[(0)]["winddirection"])))
            self["bigweathertype1"].setText(icontotext(str(dataPerUur[(0)]["iconcode"])))
        except:
            0+0

        try:
            alertKleur, alertTekst = localWeatherAlert(dataDagen[0])
        except Exception as e:
            alertKleur, alertTekst = "", ""
            print("updateFrameselect: fout bij bepalen weeralarm:", e)
        if alertTekst:
            kleurwaarde = {
                "yellow": gRGB(0xf2c200),
                "orange": gRGB(0xff8c00),
                "red":    gRGB(0xe02020),
                "blue":   gRGB(0x40a0ff),
            }.get(alertKleur, gRGB(0xffffff))
            self["weatheralert1"].setText(alertTekst)
            try:
                if self["weatheralert1"].instance is not None:
                    self["weatheralert1"].instance.setForegroundColor(kleurwaarde)
            except Exception as e:
                print("updateFrameselect: fout bij instellen weeralarm-kleur:", e)
            try:
                if sz_w > 1800:
                    iconpad = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/alert/alert_" + alertKleur + ".png"
                else:
                    iconpad = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/alert/alert_" + alertKleur + "_sd.png"
                if self["weatheralerticon1"].instance is not None:
                    self["weatheralerticon1"].instance.setPixmapFromFile(iconpad)
                    self["weatheralerticon1"].show()
            except Exception as e:
                print("updateFrameselect: fout bij laden alert-icoon:", e)
                self["weatheralerticon1"].hide()
            self["weatheralertbg1"].show()
        else:
            self["weatheralert1"].setText("")
            self["weatheralerticon1"].hide()
            self["weatheralertbg1"].hide()

        feeltext = "na"
        if dataDagen[0].get("feeltemperature"):
            feeltext = dataDagen[0]["feeltemperature"]

        windtext = "na"
        if dataDagen[0].get("winddirection"):
            windtext = dataDagen[0]["winddirection"]

        typetext = "na"
        if dataDagen[0].get("iconcode"):
            typetext = dataDagen[0]["iconcode"]

        dataPerUur = weatherData["days"][self.selected]["hours"]
        self["bigWeerIcon1" + str(0)].show()
        self["bigDirIcon1" + str(0)].show()

        slotHours = self.getSlotHours(self.selected)

        for perUurUpdate in range(0, 8):
            for day in range(0, 7):
                self["dayIcon" + str(day) + str(perUurUpdate)].hide()
            self["vlakuur" + str(perUurUpdate)].hide()
            self["sunicon" + str(perUurUpdate)].hide()
            self["rainicon" + str(perUurUpdate)].hide()
            self["rhicon" + str(perUurUpdate)].hide()
            self["windicon" + str(perUurUpdate)].hide()

            slotHasData = perUurUpdate < len(slotHours)

            if slotHasData:
                self["dayIcon" + str(self.selected) + str(perUurUpdate)].show()
                self["vlakuur" + str(perUurUpdate)].show()
                self["sunicon" + str(perUurUpdate)].show()
                iconfolder = "iconhd" if sz_w > 1800 else "icon"
                iconpath = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/" + iconfolder + "/" + slotHours[perUurUpdate]["iconcode"] + ".png"
                try:
                    self["dayIcon" + str(self.selected) + str(perUurUpdate)].instance.setPixmap(loadPNG(iconpath))
                except:
                    pass
                self["rainicon" + str(perUurUpdate)].show()
                self["rhicon" + str(perUurUpdate)].show()
                self["windicon" + str(perUurUpdate)].show()

            try:
                if slotHasData:
                    entry = slotHours[perUurUpdate]
                    self["dayhour3" + str(perUurUpdate)].setText(str(entry["hour"]) + _("h"))
                    self["daytemp3" + str(perUurUpdate)].setText('{:>4}'.format(str("%.0f" % entry["temperature"]) + "\xb0C"))
                    self["daypercent3" + str(perUurUpdate)].setText(str(entry["precipation"]) + "%")
                    self["dayspeed3" + str(perUurUpdate)].setText(str(entry["windspeed"]) + _("Km/h"))
                    self["sunpercent3" + str(perUurUpdate)].setText(str(entry["sunshine"]) + "%")
                    self["hrdayper3" + str(perUurUpdate)].setText(str(entry["humidity"]) + "%")
                else:
                    self["dayhour3" + str(perUurUpdate)].setText("")
                    self["daytemp3" + str(perUurUpdate)].setText("")
                    self["daypercent3" + str(perUurUpdate)].setText("")
                    self["dayspeed3" + str(perUurUpdate)].setText("")
                    self["sunpercent3" + str(perUurUpdate)].setText("")
                    self["hrdayper3" + str(perUurUpdate)].setText("")
            except:
                try:
                    if slotHasData:
                        entry = slotHours[perUurUpdate]
                        self["dayhour3" + str(perUurUpdate)].setText(str(entry["hour"]) + _("h"))
                        self["daytemp3" + str(perUurUpdate)].setText('{:>4}'.format(str("%.0f" % entry["temperature"]) + "\xb0C"))
                        self["daypercent3" + str(perUurUpdate)].setText(str(entry["precipitation"]) + "%")
                        self["dayspeed3" + str(perUurUpdate)].setText(str(entry["windspeed"]) + _("Km/h"))
                        self["sunpercent3" + str(perUurUpdate)].setText(str(entry["sunshine"]) + "%")
                        self["hrdayper3" + str(perUurUpdate)].setText(str(entry["humidity"]) + "%")
                    else:
                        self["dayhour3" + str(perUurUpdate)].setText("")
                        self["daytemp3" + str(perUurUpdate)].setText("")
                        self["daypercent3" + str(perUurUpdate)].setText("")
                        self["dayspeed3" + str(perUurUpdate)].setText("")
                        self["sunpercent3" + str(perUurUpdate)].setText("")
                        self["hrdayper3" + str(perUurUpdate)].setText("")
                except:
                    self["dayIcon" + str(self.selected) + str(perUurUpdate)].hide()
                    self["vlakuur" + str(perUurUpdate)].hide()
                    self["sunicon" + str(perUurUpdate)].hide()
                    self["rainicon" + str(perUurUpdate)].hide()
                    self["rhicon" + str(perUurUpdate)].hide()
                    self["windicon" + str(perUurUpdate)].hide()

    def KeyMenu(self):
        self.session.open(localcityscreen)

    def left(self):
        self.selected -= 1
        self.updateFrameselect()

    def right(self):
        self.selected += 1
        self.updateFrameselect()

    def fourteendays(self):
        self.session.open(fourteen)

    def loadBackground(self):
        global backgroundpath, icoonpath
        if not hasattr(self, 'picload') or self.picload is None:
            return
        if backgroundpath and os.path.exists(backgroundpath):
            bgfile = backgroundpath
        else:
            if sz_w > 1800:
                bgfile = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/backgroundhd.png"
            else:
                bgfile = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/background.png"
        try:
            if sz_w > 1800:
                self.picload.setPara([1920, 1080, 1, 1, False, 1, "#ff000000"])
            else:
                self.picload.setPara([1280, 720, 1, 1, False, 1, "#ff000000"])
            self.picload.startDecode(bgfile)
        except Exception as e:
            print("loadBackground: fout bij laden achtergrond:", e)

    def bgPictureLoaded(self, picInfo=None):
        if not hasattr(self, 'picload') or self.picload is None:
            return
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["bgpic"].instance.setPixmap(ptr)
                self["bgpic"].show()
        except Exception as e:
            print("bgPictureLoaded: fout:", e)

    #Temporary button for the backgrounds
    def openBackgroundPicker(self):
        self.session.openWithCallback(self.backgroundPickerCallback, BackgroundPickerScreen)

    #Temporary button for the twolocations
    def openTwoLocations(self):
        self.session.open(twolocations)

    def backgroundPickerCallback(self, changed=None):
        # Background reload, without restart
        if changed:
            self.loadBackground()

    def exit(self):
        ClosePlugin()

    def cancel(self):
        ClosePlugin()


class fourteen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        global weatherData
        if sz_w > 1800:
            dayinfoblok = ""
            lines_size = {'-1.png': [122, 15], '-2.png': [122, 30], '-3.png': [122, 45], '-4.png': [122, 60], '-5.png': [122, 75], '-6.png': [122, 90], '-7.png': [122, 105], '-8.png': [122, 120], '-9.png': [122, 135], '-10.png': [122, 150], '-11.png': [122, 165], '-12.png': [122, 180], '-13.png': [122, 195], '-14.png': [122, 210], '-15.png': [122, 225], '0.png': [122, 5], '1.png': [122, 15], '2.png': [122, 30], '3.png': [122, 45], '4.png': [122, 60], '5.png': [122, 75], '6.png': [122, 90], '7.png': [122, 105], '8.png': [122, 120], '9.png': [122, 135], '10.png': [122, 150], '11.png': [122, 165], '12.png': [122, 180], '13.png': [122, 195], '14.png': [122, 210], '15.png': [122, 225], 'b-1.png': [122, 15], 'b-2.png': [122, 30], 'b-3.png': [122, 45], 'b-4.png': [122, 60], 'b-5.png': [122, 75], 'b-6.png': [122, 90], 'b-7.png': [122, 105], 'b-8.png': [122, 120], 'b-9.png': [122, 135], 'b-10.png': [122, 150], 'b-11.png': [122, 165], 'b-12.png': [122, 180], 'b-13.png': [122, 195], 'b-14.png': [122, 210], 'b-15.png': [122, 225], 'b0.png': [122, 5], 'b1.png': [122, 15], 'b2.png': [122, 30], 'b3.png': [122, 45], 'b4.png': [122, 60], 'b5.png': [122, 75], 'b6.png': [122, 90], 'b7.png': [122, 105], 'b8.png': [122, 120], 'b9.png': [122, 135], 'b10.png': [122, 150], 'b11.png': [122, 165], 'b12.png': [122, 180], 'b13.png': [122, 195], 'b14.png': [122, 210], 'b15.png': [122, 225]}
            dataDagen = weatherData["days"]
            maxheightshift = 2000
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 15
                yposline = (1200-(curtemp * 15))-lineheight
                yposline = (((yposline) + lineheight) - 12)
                if yposline < maxheightshift:
                    maxheightshift = yposline
            maxheightshift = 700-maxheightshift
            maxlowertemp = 0
            maxlowertempmover = 0
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 15
                yposline = (1200-(curtemp * 15))-lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"]) * 2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline + maxheightshift

                tempdiffcold = 0
                curtemp = int(round(dagenbefore["mintemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiffcold = int(round(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheightcold = 0
                if tempdiffcold > 0:
                    lineheightcold = tempdiffcold * 15
                yposlinecold = (1200-(curtemp*15)) - lineheightcold
                yposlinecold = yposlinecold+maxheightshift
                thatdaymin = (yposlinecold + 15) + lineheightcold + 54  # take 60 if hight of the linetempmin-label is too low (HD)
                if thatdaymin > maxlowertemp:
                    maxlowertemp = thatdaymin
            if maxlowertemp > sz_h:
                maxlowertempmover = maxlowertemp- sz_h
            
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 15
                yposline = (1200-(curtemp * 15))-lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"]) * 2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline + maxheightshift

                tempdiffcold = 0
                curtemp = int(round(dagenbefore["mintemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiffcold = int(round(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheightcold = 0
                if tempdiffcold > 0:
                    lineheightcold = tempdiffcold * 15
                yposlinecold = (1200-(curtemp*15)) - lineheightcold
                yposlinecold = yposlinecold+maxheightshift

                tempdiff = max(-15, min(15, tempdiff))
                tempdiffcold = max(-15, min(15, tempdiffcold))

                if day < (len(dataDagen) - 1):
                    linesize = """size="%s,%s\"""" % (lines_size[(str(tempdiff) + ".png")][0], lines_size[(str(tempdiff) + ".png")][1])
                    linesizeb = """size="%s,%s\"""" % (lines_size["b" + (str(tempdiffcold) + ".png")][0], lines_size[(str(tempdiffcold) + ".png")][1])
                    dayinfoblok += """
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/""" + str(tempdiff) + """.png" position=\"""" + str((130 + (118 * day)) + 59) + """,""" + str(yposline) + """\" """+linesize+""" zPosition="10" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/b""" + str(tempdiffcold) + """.png" position=\"""" + str((130 + (118 * day)) + 59) + """,""" + str(yposlinecold-maxlowertempmover) + """\" """+linesizeb+""" zPosition="10" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/bar.png" position=\"""" + str((130 + (118 * day)) + 120) + """,140" size="10,900" zPosition="10" transparent="0" alphatest="blend"/>
                    """

                closedrainbar = int(round(rainamount/3)*3)
                dayinfoblok += """
                    <widget render="Label" source="regenval""" + str(day) + """" position=\"""" + str((134 + (118 * day)) + 0) + """,600" size="118,54" valign="center" halign="center" zPosition="20" font="Regular;25" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="windspeed""" + str(day) + """" position=\"""" + str((134 + (118 * day)) + 0) + """,435" size="118,54" valign="center" halign="center" zPosition="20" font="Regular;25" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="regenvalunit""" + str(day) + """" position=\"""" + str((134 + (118 * day)) + 0) + """,600" size="118,54" valign="center" halign="center" zPosition="20" font="Regular;30" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/rain_""" + str(closedrainbar) + """.png" position=\"""" + str((128 + (118 * day)) + 45) + """,""" + str((602) - closedrainbar) + """\" size="60,""" + str(closedrainbar) + """\" zPosition="12" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/rainstond.png" position=\"""" + str((110 + (118 * day)) + 45) + """,""" + str((600)) + """\" size="80,10" zPosition="15" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/rdot.png" position=\"""" + str(((130 + (118 * day)) + 59)-12) + """,""" + str((((yposline) + lineheight)-12)) + """\" size="25,25" zPosition="10" transparent="0" alphatest="blend"/>
                    <widget name="bigWeerIcon1""" + str(day) + """" position=\"""" + str((130 + (118 * day)) + 28) + """,267" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/iconhd/""" + str(dagenbefore["iconcode"]) + """.png" zPosition="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/lines/bdot.png" position=\"""" + str(((130 + (118 * day)) + 59)-12) + """,""" + str(((yposlinecold) + lineheightcold)-12-maxlowertempmover) + """\" size="25,25" zPosition="10" transparent="0" alphatest="blend"/>
                    <widget name="wind""" + str(day) + """" position=\"""" + str((130 + (118 * day)) + 40) + """,375" size="56,56" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windbig/""" + str(dagenbefore["winddirection"]) + """.png" zPosition="2" transparent="1" alphatest="blend"/>
                    <widget render="Label" source="dagvandeweek""" + str(day) + """" position=\"""" + str((134 + (118 * day)) + 0) + """,155" size="118,54" valign="center" halign="center" zPosition="15" font="Regular;45" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="datumvandeweek""" + str(day) + """" position=\"""" + str((134 + (118 * day)) + 0) + """,195" size="118,54" valign="center" halign="center" zPosition="15" font="Regular;30" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="linetempmax""" + str(day) + """" position=\"""" + str(((130 + (118 * day))-15) + 59) + """,""" + str(((yposline-45) + lineheight)) + """\" size="90,54" zPosition="15" font="Regular;30" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="linetempmin""" + str(day) + """" position=\"""" + str(((130 + (118 * day))-15) + 59) + """,""" + str((yposlinecold + 15) + lineheightcold-maxlowertempmover) + """\" size="90,54" zPosition="15" font="Regular;30" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    """
            skin = """
                    <screen name="fourteen" position="center,center" size="1920,1080" title="fourteen">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/bgbluhd.png" position="center,center" size="1920,1080" zPosition="0" alphatest="blend"/>
                    <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget render="Label" source="city1" position="608,44" size="705,64" zPosition="3" valign="center" halign="center" font="Regular;48" transparent="1" />
                    """ + dayinfoblok + """
                    </screen>"""

            # for day in range(0, 14):
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*15
                yposline = (1200-(curtemp*15))-lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"])*2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline+maxheightshift

                self["windspeed" + str(day)] = StaticText()
                self["windspeed" + str(day)].text = windspeed_with_beaufort(dagenbefore["windspeed"])
                self["regenval" + str(day)] = StaticText()
                self["regenval" + str(day)].text = str(dagenbefore["precipitationmm"]) + " mm"
                self["regenvalunit" + str(day)] = StaticText()
                self["regenvalunit" + str(day)].text = str("")
                curtempcold = int(round(dagenbefore["mintemperature"]))
                self["linetempmax" + str(day)] = StaticText()
                self["linetempmax" + str(day)].text = str(curtemp)
                self["linetempmin" + str(day)] = StaticText()
                self["linetempmin" + str(day)].text = str(curtempcold)
                if day < 14:

                    mydate = dagenbefore["date"][:-9]
                    unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
                    unixtimecode = unixtimecode
                    info1 = _(str(strftime("%A", localtime(unixtimecode))).title()[:2])
                    info2 = str(strftime("%d-%m", localtime(unixtimecode)))

                self["bigWeerIcon1" + str(day)] = Pixmap()
                self["wind" + str(day)] = Pixmap()
                self["city1"] = StaticText()
                self["city1"].text = str(citynamedisplay)
                self["dagvandeweek" + str(day)] = StaticText()
                self["dagvandeweek" + str(day)].text = str(info1).upper()
                self["datumvandeweek" + str(day)] = StaticText()
                self["datumvandeweek" + str(day)].text = str(info2)
        else:
            dayinfoblok = ""
            lines_size = {'-1.png': [82, 10], '-2.png': [82, 20], '-3.png': [82, 30], '-4.png': [82, 40], '-5.png': [82, 50], '-6.png': [82, 60], '-7.png': [82, 70], '-8.png': [82, 80], '-9.png': [82, 90], '-10.png': [82, 100], '-11.png': [82, 110], '-12.png': [82, 120], '-13.png': [82, 130], '-14.png': [82, 140], '-15.png': [82, 150], '0.png': [82, 3], '1.png': [82, 10], '2.png': [82, 20], '3.png': [82, 30], '4.png': [82, 40], '5.png': [82, 50], '6.png': [82, 60], '7.png': [82, 70], '8.png': [82, 80], '9.png': [82, 90], '10.png': [82, 100], '11.png': [82, 110], '12.png': [82, 120], '13.png': [82, 130], '14.png': [82, 140], '15.png': [82, 150], 'b-1.png': [82, 10], 'b-2.png': [82, 20], 'b-3.png': [82, 30], 'b-4.png': [82, 40], 'b-5.png': [82, 50], 'b-6.png': [82, 60], 'b-7.png': [82, 70], 'b-8.png': [82, 80], 'b-9.png': [82, 90], 'b-10.png': [82, 110], 'b-11.png': [82, 110], 'b-12.png': [82, 120], 'b-13.png': [82, 130], 'b-14.png': [82, 140], 'b-15.png': [82, 150], 'b0.png': [82, 3], 'b1.png': [82, 10], 'b2.png': [82, 20], 'b3.png': [82, 30], 'b4.png': [82, 40], 'b5.png': [82, 50], 'b6.png': [82, 60], 'b7.png': [82, 70], 'b8.png': [82, 80], 'b9.png': [82, 90], 'b10.png': [82, 100], 'b11.png': [82, 110], 'b12.png': [82, 120], 'b13.png': [82, 130], 'b14.png': [82, 140], 'b15.png': [82, 150]}
            dataDagen = weatherData["days"]
            maxheightshift = 1333
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 10
                yposline = (800 - (curtemp * 10))-lineheight
                yposline = (((yposline) + lineheight) - 12)
                if yposline < maxheightshift:
                    maxheightshift = yposline
            maxheightshift = 467 - maxheightshift
            
            maxlowertemp = 0
            maxlowertempmover = 0
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 10
                yposline = (800 - (curtemp * 10)) - lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"]) * 2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline+maxheightshift

                tempdiffcold = 0
                curtemp = int(round(dagenbefore["mintemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiffcold = int(round(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheightcold = 0
                if tempdiffcold > 0:
                    lineheightcold = tempdiffcold * 10
                yposlinecold = (800-(curtemp*10)) - lineheightcold
                yposlinecold = yposlinecold + maxheightshift           
                thatdaymin = (yposlinecold + 10) + lineheightcold + 36  # take 40 if hight of the linetempmin-label is too low (SD)
                if thatdaymin > maxlowertemp:
                    maxlowertemp = thatdaymin
            if maxlowertemp > sz_h:
                maxlowertempmover = maxlowertemp- sz_h
            
            
            
            
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff * 10
                yposline = (800 - (curtemp * 10)) - lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"]) * 2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline+maxheightshift

                tempdiffcold = 0
                curtemp = int(round(dagenbefore["mintemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiffcold = int(round(dataDagen[day + 1]["mintemperature"]) - curtemp)
                lineheightcold = 0
                if tempdiffcold > 0:
                    lineheightcold = tempdiffcold * 10
                yposlinecold = (800-(curtemp*10)) - lineheightcold
                yposlinecold = yposlinecold + maxheightshift

                tempdiff = max(-15, min(15, tempdiff))
                tempdiffcold = max(-15, min(15, tempdiffcold))

                if day < (len(dataDagen) - 1):
                    linesize = """size="%s,%s\"""" % (lines_size[(str(tempdiff) + ".png")][0], lines_size[(str(tempdiff) + ".png")][1])
                    linesizeb = """size="%s,%s\"""" % (lines_size["b" + (str(tempdiffcold) + ".png")][0], lines_size[(str(tempdiffcold) + ".png")][1])
                    dayinfoblok += """
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/""" + str(tempdiff) + """.png" position=\"""" + str((86 + (79 * day)) + 39) + """,""" + str(yposline) + """\" """+linesize+""" zPosition="10" transparent="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/b""" + str(tempdiffcold) + """.png" position=\"""" + str((86 + (79 * day)) + 39) + """,""" + str(yposlinecold-maxlowertempmover) + """\" """+linesizeb+""" zPosition="10" transparent="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/bar.png" position=\"""" + str((86 + (79 * day)) + 80) + """,93" size="3,590" zPosition="10" transparent="0" alphatest="blend"/>
                    """

                closedrainbar = int(round(rainamount/3)*3)
                dayinfoblok += """
                    <widget render="Label" source="regenval""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 0) + """,400" size="79,36" valign="center" halign="center" zPosition="20" font="Regular;17" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="windspeed""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 0) + """,278" size="79,48" valign="center" halign="center" zPosition="20" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="regenvalunit""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 0) + """,400" size="79,36" valign="center" halign="center" zPosition="20" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/rain_""" + str(closedrainbar) + """.png" position=\"""" + str((80 + (79 * day)) + 30) + """,""" + str((405) - closedrainbar) + """\" size="40,""" + str(closedrainbar) + """\" zPosition="12" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/rainstond.png" position=\"""" + str((64 + (79 * day)) + 30) + """,""" + str((400)) + """\" size="67,7" zPosition="15" transparent="0" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/rdot.png" position=\"""" + str(((87 + (79 * day)) + 39)-8) + """,""" + str((((yposline) + lineheight)-8)) + """\" size="18,18" zPosition="10" transparent="0" alphatest="blend"/>
                    <widget name="bigWeerIcon1""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 19) + """,178" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/icon/""" + str(dagenbefore["iconcode"]) + """.png" zPosition="1" alphatest="blend"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/linessd/bdot.png" position=\"""" + str(((87 + (79 * day)) + 39)-8) + """,""" + str(((yposlinecold) + lineheightcold)-8-maxlowertempmover) + """\" size="18,18" zPosition="10" transparent="0" alphatest="blend"/>
                    <widget name="wind""" + str(day) + """" position=\"""" + str((80 + (79 * day)) + 27) + """,250" size="42,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/windhd/""" + str(dagenbefore["winddirection"]) + """.png" zPosition="2" transparent="1" alphatest="blend"/>
                    <widget render="Label" source="dagvandeweek""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 0) + """,103" size="79,36" valign="center" halign="center" zPosition="15" font="Regular;30" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="datumvandeweek""" + str(day) + """" position=\"""" + str((87 + (79 * day)) + 0) + """,130" size="79,36" valign="center" halign="center" zPosition="15" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="linetempmax""" + str(day) + """" position=\"""" + str(((103 + (79 * day))-10) + 26) + """,""" + str(((yposline-35) + lineheight)) + """\" size="60,36" zPosition="15" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget render="Label" source="linetempmin""" + str(day) + """" position=\"""" + str(((106 + (79 * day))-10) + 26) + """,""" + str((yposlinecold + 10) + lineheightcold-maxlowertempmover) + """\" size="60,36" zPosition="15" font="Regular;20" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    """
            skin = """
                    <screen name="fourteen" position="center,center" size="1280,720" title="fourteen">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/bgblusd.png" position="center,center" size="1280,720" zPosition="0" alphatest="blend"/>
                    <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget render="Label" source="city1" position="406,30" size="470,43" zPosition="3" valign="center" halign="center" font="Regular;32" transparent="1" />
                    """ + dayinfoblok + """
                    </screen>"""
            # for day in range(0, 14):
            for day in range(0, len(dataDagen)):
                dagenbefore = dataDagen[day]
                tempdiff = 0
                curtemp = int(round(dagenbefore["maxtemperature"]))
                if (day+1) < len(dataDagen):
                    tempdiff = int(round(dataDagen[day + 1]["maxtemperature"]) - curtemp)
                lineheight = 0
                if tempdiff > 0:
                    lineheight = tempdiff*10
                yposline = (800-(curtemp*10))-lineheight
                shiftstart = 130
                rainamount = (int(float(dagenbefore["precipitationmm"])*2))
                if rainamount > 1 and rainamount < 10:
                    rainamount = 10
                if rainamount > 100:
                    rainamount = 100
                yposline = yposline+maxheightshift

                self["windspeed" + str(day)] = StaticText()
                self["windspeed" + str(day)].text = windspeed_with_beaufort(dagenbefore["windspeed"])
                self["regenval" + str(day)] = StaticText()
                self["regenval" + str(day)].text = str(dagenbefore["precipitationmm"]) + " mm"
                self["regenvalunit" + str(day)] = StaticText()
                self["regenvalunit" + str(day)].text = str("")
                curtempcold = int(round(dagenbefore["mintemperature"]))
                self["linetempmax" + str(day)] = StaticText()
                self["linetempmax" + str(day)].text = str(curtemp)
                self["linetempmin" + str(day)] = StaticText()
                self["linetempmin" + str(day)].text = str(curtempcold)
                if day < 14:

                    mydate = dagenbefore["date"][:-9]
                    unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
                    unixtimecode = unixtimecode
                    info1 = _(str(strftime("%A", localtime(unixtimecode))).title()[:2])
                    info2 = str(strftime("%d-%m", localtime(unixtimecode)))

                self["bigWeerIcon1" + str(day)] = Pixmap()
                self["wind" + str(day)] = Pixmap()
                self["city1"] = StaticText()
                self["city1"].text = str(citynamedisplay)
                self["dagvandeweek" + str(day)] = StaticText()
                self["dagvandeweek" + str(day)].text = str(info1).upper()
                self["datumvandeweek" + str(day)] = StaticText()
                self["datumvandeweek" + str(day)].text = str(info2)
        self.session = session
        self.skin = skin
        self["myActionMap"] = ActionMap(["SetupActions"], {"ok": self.dayseven, "cancel": self.cancel, "red": self.exit}, -1)

    def dayseven(self):
        self.close()

    def exit(self):
        self.close()

    def cancel(self):
        self.close()


class localcityscreen(Screen):

    def __init__(self, session):
        if sz_w > 1800:
            skin = """
                    <screen name="startScreen" position="center,center" size="1920,1080" title="Weather Plugin">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,112" size="1920,3" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,1010" size="1920,3" zPosition="1"/>
                    <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="3" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="3" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget source="session.VideoPicture" render="Pig" position="30,160" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
                    <widget source="session.CurrentService" render="Label" position="30,125" size="720,36" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                    <widget name="list" position="840,225" size="1000,630" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list97563.png"/>\n
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red34.png" position="192,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_red" position="242,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green34.png" position="628,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_green" position="678,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow34.png" position="1064,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_yellow" position="1114,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/blue34.png" position="1500,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_blue" position="1550,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="favor" position="85,45" size="1085,55" valign="center" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="plaatsn" position="840,135" size="375,70" valign="center" halign="left" zPosition="1" font="Regular;63" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    </screen>"""

        else:
            skin = """
                    <screen name="startScreen" position="center,center" size="1280,720" title="Weather Plugin">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,650" size="1280,2" zPosition="1"/>
                    <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget source="session.VideoPicture" render="Pig" position="85,120" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
                    <widget source="session.CurrentService" render="Label" position="85,93" size="417,32" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                    <widget name="list" position="630,156" size="600,420" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list65043.png"/>\n
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red26.png" position="145,663" size="26,26" alphatest="blend"/>
                    <widget name="key_red" position="185,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green26.png" position="420,663" size="26,26" alphatest="blend"/>
                    <widget name="key_green" position="460,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow26.png" position="695,663" size="26,26" alphatest="blend"/>
                    <widget name="key_yellow" position="735,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/blue26.png" position="970,663" size="26,26" alphatest="blend"/>
                    <widget name="key_blue" position="1010,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="favor" position="57,30" size="723,37" valign="center" halign="left" zPosition="1" font="Regular;24" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="plaatsn" position="630,90" size="250,47" valign="center" halign="left" zPosition="1" font="Regular;42" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    </screen>"""

        self.session = session
        Screen.__init__(self, session)
        self.skin = skin
        AddNewScreen(self)
        self.onClose.append(lambda: RemoveScreen(self))
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Location +"))
        self["key_yellow"] = Label(_("Location -"))
        self["key_blue"] = Label(_("Settings"))
        self["favor"] = Label(_("Favorite Locations"))
        self["plaatsn"] = Label(_("Location:"))
        self.res = []
        global SavedLokaleWeer
        for x in SavedLokaleWeer:
            cleanmadecity = str(x).split("-")[0]
            if sz_w > 1800:
                self.res.append([x, MultiContentEntryText(pos=(0, 0), size=(960, 63), font=0, flags=RT_HALIGN_LEFT, text=cleanmadecity, color_sel=0x00D2D226)])
            else:
                self.res.append([x, MultiContentEntryText(pos=(0, 0), size=(590, 42), font=0, flags=RT_HALIGN_LEFT, text=cleanmadecity, color_sel=0x00D2D226)])

        self["list"] = MenuList(self.res, True, eListboxPythonMultiContent)
        if sz_w > 1800:
            self["list"].l.setItemHeight(63)
            self['list'].l.setFont(0, gFont("Regular", 50))
        else:
            self["list"].l.setItemHeight(42)
            self['list'].l.setFont(0, gFont("Regular", 33))
        self["list"].show()
        self["actions"] = ActionMap(["WizardActions", "MenuActions", "ShortcutActions"], {"ok": self.go, "back": self.cancel}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "yellow": self.removeLoc, "green": self.addLoc, "blue": self.addcityinf}, -1)

    def go(self):
        if len(SavedLokaleWeer) > 0:
            index = self["list"].getSelectedIndex()
            selecteddat = self.res[index][0]
            try:
                if getLocWeer(selecteddat.rstrip()):
                    file = open(CFG_DIR + "/TheWeather_last.cfg", "w")
                    file.write(selecteddat)
                    file.close()
                    time.sleep(1)
                    self.session.open(sevendays)
                else:
                    self.session.open(MessageBox, _("Download error: Check spelling."), MessageBox.TYPE_INFO)
            except:
                self.session.open(MessageBox, _("Download error: No response try again"), MessageBox.TYPE_INFO)

    def addLoc(self):
        try:
            self.session.openWithCallback(self.searchCity, VirtualKeyBoard, title=_("Enter cityname e.g. london or london_gb or london-2643743"), text="")
        except:
            None
            self.session.openWithCallback(self.searchCity, VirtualKeyBoard, title=_("Enter cityname e.g. london or london_gb or london-2643743"), text="")

    def removeLoc(self):
        if len(SavedLokaleWeer) > 0:
            index = self["list"].getSelectedIndex()
            SavedLokaleWeer.remove(SavedLokaleWeer[index])
            file = open(CFG_DIR + "/TheWeather.cfg", "w")
            for x in SavedLokaleWeer:
                file.write(str(x) + "\n")
            file.close()
            self.close()
            self.close()

    def searchCity(self, searchterm=None):
        if searchterm is not None:
            searchterm = "" + searchterm.title()
            SavedLokaleWeer.append(str(searchterm))
            file = open(CFG_DIR + "/TheWeather.cfg", "w")
            for x in SavedLokaleWeer:
                file.write((str(x) + "\n"))
            file.close()
            self.close()
            self.close()

    def addcityinf(self):
        self.session.open(infoscreen)

    def exit(self):
        self.close(localcityscreen)

    def cancel(self):
        self.close(localcityscreen)


class infoscreen(Screen):
    def __init__(self, session):
        if sz_w > 1800:
            skin = """
                    <screen name="startScreen" position="center,center" size="1920,1080" title="Weather Plugin">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,112" size="1920,3" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,1010" size="1920,3" zPosition="1"/>
                    <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="3" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="3" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget source="session.VideoPicture" render="Pig" position="30,160" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
                    <widget source="session.CurrentService" render="Label" position="30,125" size="720,36" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red34.png" position="192,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_red" position="242,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green34.png" position="628,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_green" position="678,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow34.png" position="1064,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_yellow" position="1114,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/blue34.png" position="1500,1022" size="34,34" alphatest="blend"/>
                    <widget name="key_blue" position="1550,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="helpinfo" position="900,210" size="800,600" valign="top" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="helpinfo2" position="900,600" size="800,600" valign="top" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="version" position="1350,945" size="600,42" valign="center" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    </screen>"""
        else:
            skin = """
                    <screen name="startScreen" position="center,center" size="1280,720" title="Weather Plugin">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                    <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                    <widget source="session.VideoPicture" render="Pig" position="85,120" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
                    <widget source="session.CurrentService" render="Label" position="85,93" size="417,32" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red26.png" position="145,663" size="26,26" alphatest="blend"/>
                    <widget name="key_red" position="185,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green26.png" position="420,663" size="26,26" alphatest="blend"/>
                    <widget name="key_green" position="460,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow26.png" position="695,663" size="26,26" alphatest="blend"/>
                    <widget name="key_yellow" position="735,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/blue26.png" position="970,663" size="26,26" alphatest="blend"/>
                    <widget name="key_blue" position="1010,663" size="220,32" zPosition="1" font="Regular;24" halign="left" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="helpinfo" position="700,120" size="400,320" valign="top" halign="left" zPosition="1" font="Regular;20" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="helpinfo2" position="700,400" size="400,320" valign="top" halign="left" zPosition="1" font="Regular;20" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    <widget name="version" position="900,590" size="400,28" valign="center" halign="left" zPosition="1" font="Regular;20" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                    </screen>"""

        self.session = session
        Screen.__init__(self, session)
        self.skin = skin
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Standard Icons"))
        self["key_yellow"] = Label(_("Extra Icons "))
        self["key_blue"] = Label(_("Background"))
        self["helpinfo"] = Label(_("Manual adding Citynumbers:\nGo to www.bbc.com/weather\nSearch city and find citycode in the internetlink.\n\nGo back to \"Location +\" and add cityname-number e.g.\n\"Dusseldorf-2934246\" or \"Dusseld-2934246\"\nDon't forget the \"-\" sign."))
        self["helpinfo2"] = Label(_("Tip!\nPress the hidden Yellow button in the main menu to change the background.\n\nPress the hidden Green button in the main menu to change the hour interval."))
        self["actions"] = ActionMap(["WizardActions"], {"back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "green": self.default, "yellow": self.extra, "blue": self.openBackgroundPicker}, -1)
        self["version"] = Label("TheWeather_v.%s" % version)
        AddNewScreen(self)
        self.onClose.append(lambda: RemoveScreen(self))

    def exit(self):
        self.close()

    def default(self):
        self["helpinfo"].setText(_("Loading standard icons, please wait..."))
        with open(CFG_DIR + "/iconpack.cfg", "w") as f:
            f.write("Images")
        self.switchIconpackAndRestart("Images")

    def extra(self):
        self["helpinfo"].setText(_("Loading extra icons, please wait..."))
        with open(CFG_DIR + "/iconpack.cfg", "w") as f:
            f.write("Images_extra")
        self.switchIconpackAndRestart("Images_extra")

    def openBackgroundPicker(self):
        self.session.openWithCallback(self.backgroundPickerCallback, BackgroundPickerScreen)

    def backgroundPickerCallback(self, changed=None):
        pass

    def switchIconpackAndRestart(self, nieuwPad):
        global icoonpath, _restartTimer, _restartTimerConn, _restartInProgress
        if _restartInProgress:
            return
        _restartInProgress = True
        icoonpath = nieuwPad
        self.session.open(MessageBox, _("Icon pack changed.\nThe plugin will restart..."), MessageBox.TYPE_INFO, timeout=3)
        _restartTimer = eTimer()
        _restartTimerConn = safeTimerCallback(_restartTimer, self._finishIconpackRestart)
        _restartTimer.start(1500, True)

    def _finishIconpackRestart(self, ret=None):
        global _restartTimer, _restartTimerConn
        sess = self.session
        self.close()
        ClosePlugin()
        _restartTimer = eTimer()
        _restartTimerConn = safeTimerCallback(_restartTimer, lambda: _doIconpackRestart(sess))
        _restartTimer.start(50, True)


class CityPickerScreen(Screen):
    """Keuzelijst voor 2e locatie - zelfde stijl als localcityscreen."""

    def __init__(self, session, steden):
        Screen.__init__(self, session)

        if sz_w > 1800:
            skin = """
                <screen name="CityPickerScreen" position="center,center" size="1920,1080" title="Choose 2nd location">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,112" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,1010" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="3" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="3" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget source="session.VideoPicture" render="Pig" position="30,160" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
                <widget source="session.CurrentService" render="Label" position="30,125" size="720,36" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                <widget name="list" position="840,160" size="900,630" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list97563.png"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red34.png" position="192,1022" size="34,34" alphatest="blend"/>
                <widget name="key_red" position="242,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="titel" position="840,50" size="900,55" valign="center" halign="left" zPosition="1" font="Regular;44" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""
        else:
            skin = """
                <screen name="CityPickerScreen" position="center,center" size="1280,720" title="Choose 2nd location">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,650" size="1280,2" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget source="session.VideoPicture" render="Pig" position="85,120" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
                <widget source="session.CurrentService" render="Label" position="85,93" size="417,32" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
                <widget name="list" position="630,100" size="620,462" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list65043.png"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red26.png" position="145,663" size="26,26" alphatest="blend"/>
                <widget name="key_red" position="185,663" size="220,32" zPosition="1" font="Regular;24" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="titel" position="630,30" size="620,50" valign="center" halign="left" zPosition="1" font="Regular;36" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""

        self.skin = skin
        self._steden = steden
        self.res = []

        for stad in steden:
            cleanmadecity = str(stad).split("-")[0]
            if sz_w > 1800:
                self.res.append([stad, MultiContentEntryText(pos=(0, 0), size=(860, 63), font=0, flags=RT_HALIGN_LEFT, text=cleanmadecity, color_sel=0x00D2D226)])
            else:
                self.res.append([stad, MultiContentEntryText(pos=(0, 0), size=(580, 42), font=0, flags=RT_HALIGN_LEFT, text=cleanmadecity, color_sel=0x00D2D226)])

        self["list"] = MenuList(self.res, True, eListboxPythonMultiContent)
        if sz_w > 1800:
            self["list"].l.setItemHeight(63)
            self["list"].l.setFont(0, gFont("Regular", 50))
        else:
            self["list"].l.setItemHeight(42)
            self["list"].l.setFont(0, gFont("Regular", 33))
        self["list"].show()
        self["titel"] = Label(_("Choose 2nd location:"))
        self["key_red"] = Label(_("Back"))
        self["actions"] = ActionMap(["WizardActions", "MenuActions"], {
            "ok": self.selecteer,
            "back": self.annuleer,
            "cancel": self.annuleer,
        }, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {
            "red": self.annuleer,
        }, -1)

    def selecteer(self):
        idx = self["list"].getSelectedIndex()
        if 0 <= idx < len(self._steden):
            self.close(self._steden[idx])
        else:
            self.close(None)

    def annuleer(self):
        self.close(None)


class twolocations(Screen):
    
    COMPARE_CFG = CFG_DIR + "/TheWeather_compare.cfg"

    def __init__(self, session):
        Screen.__init__(self, session)
        AddNewScreen(self)
        self.onClose.append(lambda: RemoveScreen(self))

        self.compareCity = ""
        if os.path.exists(self.COMPARE_CFG):
            try:
                with open(self.COMPARE_CFG) as f:
                    val = f.read().strip()
                    if val:
                        self.compareCity = val
            except Exception:
                pass

        if sz_w > 1800:
            skin = """
                <screen name="twolocations" position="center,center" size="1920,1080" title="Compare Locations">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,112" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,980" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="958,112" size="3,868" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="3" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="3" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget name="loc1name"     position="40,125"   size="880,72"  zPosition="3" font="Regular;58" halign="center" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1icon"     position="140,215"  size="160,160" zPosition="3" alphatest="blend"/>
                <widget name="loc1maxtemp"  position="320,215"  size="380,95"  zPosition="3" font="Regular;78" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1mintemp"  position="320,310"  size="380,60"  zPosition="3" font="Regular;48" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1weertype" position="320,400"  size="600,56"  zPosition="3" font="Regular;44" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1feel"     position="320,468"  size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1wind"     position="320,530"  size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1rain"     position="320,592"  size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1sun"      position="320,654"  size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1alert"    position="320,720"  size="808,68"  zPosition="3" font="Regular;48" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1alerticon" position="216,724"  size="64,64"   zPosition="4" alphatest="blend" transparent="1"/>
                <widget name="loc2name"     position="1000,125" size="880,72"  zPosition="3" font="Regular;58" halign="center" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2icon"     position="1100,215" size="160,160" zPosition="3" alphatest="blend"/>
                <widget name="loc2maxtemp"  position="1280,215" size="380,95"  zPosition="3" font="Regular;78" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2mintemp"  position="1280,310" size="380,60"  zPosition="3" font="Regular;48" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2weertype" position="1280,400" size="600,56"  zPosition="3" font="Regular;44" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2feel"     position="1280,468" size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2wind"     position="1280,530" size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2rain"     position="1280,592" size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2sun"      position="1280,654" size="600,52"  zPosition="3" font="Regular;40" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2alert"    position="1280,720" size="808,68"  zPosition="3" font="Regular;48" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2alerticon" position="1176,724" size="64,64"  zPosition="4" alphatest="blend" transparent="1"/>
                <widget name="statusmsg"    position="40,808"   size="1840,56" zPosition="3" font="Regular;40" halign="center" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red34.png"    position="192,1022"  size="34,34" alphatest="blend"/>
                <widget name="key_red"    position="242,1015"  size="370,48" zPosition="3" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow34.png" position="628,1022"  size="34,34" alphatest="blend"/>
                <widget name="comp" position="85,45" size="1085,55" valign="center" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="key_yellow" position="678,1015"  size="600,48" zPosition="3" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""
        else:
            skin = """
                <screen name="twolocations" position="center,center" size="1280,720" title="Compare Locations">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,88"   size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,678"  size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="638,88"  size="2,590" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1090,18" size="170,40" transparent="1" zPosition="3" font="Regular;30" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="940,52"  size="320,34" transparent="1" zPosition="3" font="Regular;20" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget name="loc1name"     position="244,95"    size="618,52"  zPosition="3" font="Regular;42" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1icon"     position="104,158"   size="130,130" zPosition="3" alphatest="blend"/>
                <widget name="loc1maxtemp"  position="244,158"  size="470,80"  zPosition="3" font="Regular;72" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1mintemp"  position="244,238"  size="470,44"  zPosition="3" font="Regular;36" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1weertype" position="244,296"  size="474,44"  zPosition="3" font="Regular;34" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1feel"     position="244,348"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1wind"     position="244,394"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1rain"     position="244,440"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1sun"      position="244,486"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1alert"    position="244,538"  size="576,50"  zPosition="3" font="Regular;36" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc1alerticon" position="183,542"  size="42,42"   zPosition="4" alphatest="blend" transparent="1"/>
                <widget name="loc2name"     position="842,95"   size="618,52"  zPosition="3" font="Regular;42" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2icon"     position="702,158"  size="130,130" zPosition="3" alphatest="blend"/>
                <widget name="loc2maxtemp"  position="842,158"  size="470,80"  zPosition="3" font="Regular;72" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2mintemp"  position="842,238"  size="470,44"  zPosition="3" font="Regular;36" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2weertype" position="842,296"  size="474,44"  zPosition="3" font="Regular;34" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2feel"     position="842,348"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2wind"     position="842,394"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2rain"     position="842,440"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2sun"      position="842,486"  size="474,40"  zPosition="3" font="Regular;32" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2alert"    position="842,538"  size="576,50"  zPosition="3" font="Regular;36" halign="left" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="loc2alerticon" position="781,542" size="42,42"   zPosition="4" alphatest="blend" transparent="1"/>
                <widget name="statusmsg"    position="10,602"   size="1260,44" zPosition="3" font="Regular;30" halign="center" valign="center" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red26.png"    position="100,688" size="26,26" alphatest="blend"/>
                <widget name="key_red"    position="138,685"  size="240,32" zPosition="3" font="Regular;26" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow26.png" position="440,688" size="26,26" alphatest="blend"/>
                <widget name="comp" position="57,30" size="723,37" valign="center" halign="left" zPosition="1" font="Regular;24" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="key_yellow" position="478,685"  size="440,32" zPosition="3" font="Regular;26" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""

        self.skin = skin

        for n in ["loc1name","loc1maxtemp","loc1mintemp","loc1weertype","loc1feel","loc1wind","loc1rain","loc1sun","loc1alert",
                  "loc2name","loc2maxtemp","loc2mintemp","loc2weertype","loc2feel","loc2wind","loc2rain","loc2sun","loc2alert",
                  "statusmsg","key_red","key_yellow"]:
            self[n] = Label("")
        for n in ["loc1icon", "loc2icon", "loc1alerticon", "loc2alerticon"]:
            self[n] = Pixmap()

        self["actions"] = ActionMap(["WizardActions","MenuActions"], {"back": self.exit, "cancel": self.exit}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "yellow": self.changeCompareCity}, -1)
        self["key_red"] = Label(_("Back"))
        self["key_yellow"] = Label(_("Choose 2nd location"))
        self["comp"] = Label(_("Compare Locations"))

        self.fillLoc1()
        if self.compareCity:
            self.fillLoc2(self.compareCity)
        else:
            self._setText("loc2name", _("No 2nd location"))
            self._setText("statusmsg", _("Press YELLOW to choose a 2nd location."))

        self.iconFixTimer = eTimer()
        self._iconFixTimer_conn = safeTimerCallback(self.iconFixTimer, self.reloadIcons)
        self.iconFixTimer.start(300, True)

    def _setText(self, key, value):
        
        try:
            self[key].setText("" if value is None else str(value))
        except Exception as e:
            print("twolocations _setText fout op", key, ":", e)

    def _fillLocation(self, data, naam, prefix):
        
        try:
            dag = data["days"][0]
        except Exception:
            self._setText(prefix + "name", _("Data error"))
            return

        self._setText(prefix + "name", naam)

        try:
            curtemp = "%.1f\xb0C" % dag["hours"][0]["temperature"]
        except Exception:
            try:
                curtemp = "%.0f\xb0C" % dag["maxtemperature"]
            except Exception:
                curtemp = "--"
        self._setText(prefix + "maxtemp", curtemp)

        try:
            mintemp = "%.0f\xb0 / %.0f\xb0" % (dag["mintemperature"], dag["maxtemperature"])
        except Exception:
            mintemp = "--"
        self._setText(prefix + "mintemp", mintemp)

        try:
            self._setText(prefix + "weertype", icontotext(dag.get("iconcode", "")))
        except Exception:
            pass

        try:
            feeltemp = dag.get("feeltemperature", dag.get("maxtemperature", "--"))
            self._setText(prefix + "feel", _("Feels like: ") + "%.0f\xb0C" % float(feeltemp))
        except Exception:
            pass

        try:
            ws = dag.get("windspeed", 0)
            self._setText(prefix + "wind", _("Wind: ") + windspeed_with_beaufort(ws))
        except Exception:
            pass

        try:
            rainmm = dag.get("precipitationmm", 0)
            self._setText(prefix + "rain", _("Rain: ") + "%.1f mm" % float(rainmm))
        except Exception:
            pass

        try:
            sunrise = (str(dag.get("sunrise", "")).split("T")[1])[:-3]
            sunset  = (str(dag.get("sunset",  "")).split("T")[1])[:-3]
            self._setText(prefix + "sun", _("Sun: ") + sunrise + "  -  " + sunset)
        except Exception:
            self._setText(prefix + "sun", "")

        try:
            alertkleur, alerttekst = localWeatherAlert(dag)
            if alerttekst:
                kleurwaarde = {"yellow": gRGB(0xf2c200), "orange": gRGB(0xff8c00),
                               "red": gRGB(0xe02020), "blue": gRGB(0x40a0ff)}.get(alertkleur, gRGB(0xffffff))
                self._setText(prefix + "alert", alerttekst)
                try:
                    if self[prefix + "alert"].instance is not None:
                        self[prefix + "alert"].instance.setForegroundColor(kleurwaarde)
                except Exception:
                    pass
                try:
                    if sz_w > 1800:
                        alerticon = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/alert/alert_" + alertkleur + ".png"
                    else:
                        alerticon = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/alert/alert_" + alertkleur + "_sd.png"
                    if self[prefix + "alerticon"].instance is not None:
                        self[prefix + "alerticon"].instance.setPixmapFromFile(alerticon)
                        self[prefix + "alerticon"].show()
                except Exception:
                    self[prefix + "alerticon"].hide()
            else:
                self._setText(prefix + "alert", "")
                self[prefix + "alerticon"].hide()
        except Exception:
            pass

        try:
            iconcode = dag.get("iconcode", "")
            if sz_w > 1800:
                iconbestand = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/iconbighd/" + str(iconcode) + ".png"
            else:
                iconbestand = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/iconbigsd/" + str(iconcode) + ".png"
            try:
                if self[prefix + "icon"].instance is not None:
                    self[prefix + "icon"].instance.setPixmapFromFile(iconbestand)
            except Exception:
                pass
        except Exception:
            pass

    def reloadIcons(self):
        """Herlaad de weericonen nadat de skin volledig is toegepast."""
        self.fillLoc1()
        if self.compareCity:
            self.fillLoc2(self.compareCity)

    def fillLoc1(self):
        global weatherData, citynamedisplay
        try:
            self._fillLocation(weatherData, citynamedisplay, "loc1")
        except Exception as e:
            print("twolocations fillLoc1 fout:", e)
            self._setText("loc1name", _("Error loading"))

    def fillLoc2(self, city):
        self._setText("statusmsg", _("Loading..."))
        try:
            data, naam = getLocWeerFor(city)
            if data and naam:
                self._fillLocation(data, naam, "loc2")
                self._setText("statusmsg", "")
            else:
                self._setText("loc2name", _("Not found"))
                self._setText("statusmsg", _("City not found. Press YELLOW to change."))
        except Exception as e:
            print("twolocations fillLoc2 fout:", e)
            self._setText("loc2name", _("Error loading"))
            self._setText("statusmsg", _("Error fetching data."))

    def changeCompareCity(self):
        global SavedLokaleWeer
        if not SavedLokaleWeer:
            self.session.open(MessageBox, _("No saved cities found.\nFirst add cities via the location screen."), MessageBox.TYPE_INFO)
            return
        self.session.openWithCallback(self.onCompareCityChosen, CityPickerScreen, SavedLokaleWeer)

    def onCompareCityChosen(self, stadcode=None):
        if not stadcode:
            return
        self.compareCity = stadcode
        try:
            with open(self.COMPARE_CFG, "w") as f:
                f.write(self.compareCity)
        except Exception as e:
            print("twolocations: opslaan 2e stad mislukt:", e)
        self.fillLoc2(self.compareCity)

    def exit(self):
        self.close()


class BackgroundPickerScreen(Screen):
    """Keuzelijst voor achtergrondafbeeldingen - zelfde stijl als CityPickerScreen.
    Scant de backgrounds/-map binnen de plugin en laat de gebruiker kiezen.
    De keuze wordt opgeslagen in /etc/enigma2/TheWeather_bg.cfg."""

    BG_CFG = CFG_DIR + "/TheWeather_bg.cfg"
    BG_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/backgrounds/"
    EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")

    def __init__(self, session):
        Screen.__init__(self, session)

        if sz_w > 1800:
            skin = """
                <screen name="BackgroundPickerScreen" position="center,center" size="1920,1080" title="Choose Background">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,112" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline3.png" position="0,1010" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1634,35" size="225,45" transparent="1" zPosition="3" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1409,74" size="450,37" transparent="1" zPosition="3" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget name="preview" position="30,160" size="720,405" zPosition="1" alphatest="blend"/>
                <widget name="list" position="840,160" size="900,630" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list97563.png"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red34.png" position="192,1022" size="34,34" alphatest="blend"/>
                <widget name="key_red" position="242,1015" size="370,48" zPosition="1" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green34.png" position="628,1022" size="34,34" alphatest="blend"/>
                <widget name="key_green" position="678,1015" size="600,48" zPosition="1" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow34.png" position="1200,1022" size="34,34" alphatest="blend"/>
                <widget name="key_yellow" position="1250,1015" size="600,48" zPosition="1" font="Regular;40" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="titel" position="85,45" size="1085,55" valign="center" halign="left" zPosition="1" font="Regular;36" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""
        else:
            skin = """
                <screen name="BackgroundPickerScreen" position="center,center" size="1280,720" title="Choose Background">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/borders/smallline2.png" position="0,650" size="1280,2" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1091,12" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="941,32" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Format:%a %d/%m/%y</convert></widget>
                <widget name="preview" position="20,110" size="417,243" zPosition="1" alphatest="blend"/>
                <widget name="list" position="630,100" size="650,530" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/list/list65043.png"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/red26.png" position="50,663" size="26,26" alphatest="blend"/>
                <widget name="key_red" position="90,663" size="180,32" zPosition="1" font="Regular;24" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/green26.png" position="320,663" size="26,26" alphatest="blend"/>
                <widget name="key_green" position="360,663" size="280,32" zPosition="1" font="Regular;24" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/""" + icoonpath + """/buttons/yellow26.png" position="700,663" size="26,26" alphatest="blend"/>
                <widget name="key_yellow" position="735,663" size="280,32" zPosition="1" font="Regular;24" halign="left" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                <widget name="titel" position="57,30" size="723,37" valign="center" halign="left" zPosition="1" font="Regular;24" backgroundColor="#000000" transparent="1" shadowColor="black" shadowOffset="-2,-2"/>
                </screen>"""

        self.skin = skin

        self._bestanden = []
        if os.path.isdir(self.BG_DIR):
            for f in sorted(os.listdir(self.BG_DIR)):
                if f.lower().endswith(self.EXTENSIONS):
                    self._bestanden.append(os.path.join(self.BG_DIR, f))

        self._bestanden.insert(0, "")

        self.res = []
        for pad in self._bestanden:
            naam = _("Standard (iconpack)") if pad == "" else os.path.basename(pad)
            if sz_w > 1800:
                self.res.append([pad, MultiContentEntryText(pos=(0, 0), size=(860, 63), font=0, flags=RT_HALIGN_LEFT, text=naam, color_sel=0x00D2D226)])
            else:
                self.res.append([pad, MultiContentEntryText(pos=(0, 0), size=(580, 42), font=0, flags=RT_HALIGN_LEFT, text=naam, color_sel=0x00D2D226)])

        self["list"] = MenuList(self.res, True, eListboxPythonMultiContent)
        if sz_w > 1800:
            self["list"].l.setItemHeight(63)
            self["list"].l.setFont(0, gFont("Regular", 50))
        else:
            self["list"].l.setItemHeight(42)
            self["list"].l.setFont(0, gFont("Regular", 33))
        self["list"].show()

        self["titel"] = Label(_("Choose background:"))
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Select"))
        self["key_yellow"] = Label(_("Standard"))
        self["preview"] = Pixmap()

        self["actions"] = ActionMap(["WizardActions", "MenuActions"], {
            "ok": self.selecteer,
            "back": self.annuleer,
            "cancel": self.annuleer,
            "up": self.omhoog,
            "down": self.omlaag,
        }, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {
            "red": self.annuleer,
            "green": self.selecteer,
            "yellow": self.resetStandaard,
        }, -1)

        # Preview-loader
        self.picload = ePicLoad()
        self._preview_picload_conn = safeSignalConnect(self.picload.PictureData, self.previewLoaded)

        self.previewTimer = eTimer()
        self._previewTimer_conn = safeTimerCallback(self.previewTimer, self.laadPreview)
        self.previewTimer.start(400, True)

        global backgroundpath
        if backgroundpath in self._bestanden:
            idx = self._bestanden.index(backgroundpath)
            self["list"].moveToIndex(idx)

    def omhoog(self):
        self["list"].up()
        self.previewTimer.start(300, True)

    def omlaag(self):
        self["list"].down()
        self.previewTimer.start(300, True)

    def laadPreview(self):
        idx = self["list"].getSelectedIndex()
        pad = self._bestanden[idx] if idx < len(self._bestanden) else ""
        if not pad:
            if sz_w > 1800:
                pad = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/backgroundhd.png"
            else:
                pad = "/usr/lib/enigma2/python/Plugins/Extensions/TheWeather/" + icoonpath + "/background.png"
        try:
            if sz_w > 1800:
                self.picload.setPara([720, 405, 1, 1, False, 1, "#ff000000"])
            else:
                self.picload.setPara([417, 243, 1, 1, False, 1, "#ff000000"])
            self.picload.startDecode(pad)
        except Exception as e:
            print("BackgroundPicker laadPreview fout:", e)

    def previewLoaded(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["preview"].instance.setPixmap(ptr)
                self["preview"].show()
        except Exception as e:
            print("BackgroundPicker previewLoaded fout:", e)

    def _backToSevendays(self):
        for scr in list(screens):
            if scr is self:
                continue
            if isinstance(scr, sevendays):
                try:
                    scr.loadBackground()
                except Exception as e:
                    print("BackgroundPicker: kon achtergrond van sevendays niet verversen:", e)
            else:
                try:
                    scr.close()
                except Exception as e:
                    print("BackgroundPicker: kon tussenliggend scherm niet sluiten:", e)

    def selecteer(self):
        global backgroundpath
        idx = self["list"].getSelectedIndex()
        pad = self._bestanden[idx] if idx < len(self._bestanden) else ""
        backgroundpath = pad
        try:
            with open(self.BG_CFG, "w") as f:
                f.write(pad)
        except Exception as e:
            print("BackgroundPicker: opslaan mislukt:", e)
        self._backToSevendays()
        self.session.open(MessageBox, _("Loading background image, please wait..."), MessageBox.TYPE_INFO, timeout=4)
        self.close(True)

    def resetStandaard(self):
        global backgroundpath
        backgroundpath = ""
        try:
            with open(self.BG_CFG, "w") as f:
                f.write("")
        except Exception as e:
            print("BackgroundPicker: reset mislukt:", e)
        self._backToSevendays()
        self.session.open(MessageBox, _("Background reset to standard."), MessageBox.TYPE_INFO, timeout=2)
        self.close(True)

    def annuleer(self):
        self.close(False)


def AddNewScreen(screen):
    screens.append(screen)


def RemoveScreen(screen):
    try:
        screens.remove(screen)
    except ValueError:
        pass


def ClosePlugin():
    for screen in list(screens):
        try:
            screen.close()
        except:
            None
    del screens[:]


def safeSignalConnect(sig, func):
    if hasattr(sig, "get"):
        try:
            sig.get().append(func)
            return None
        except Exception as e:
            print("[TheWeather] safeSignalConnect: .get().append faalde:", e)

    if hasattr(sig, "connect"):
        try:
            return sig.connect(func)
        except Exception as e:
            print("[TheWeather] safeSignalConnect: .connect faalde:", e)

    try:
        from enigma import eConnectCallback
        return eConnectCallback(sig, func)
    except Exception as e:
        print("[TheWeather] safeSignalConnect: eConnectCallback faalde:", e)

    try:
        sig.append(func)
        return None
    except Exception as e:
        print("[TheWeather] safeSignalConnect: .append faalde:", e)

    print("[TheWeather] safeSignalConnect: GEEN methode werkte. beschikbare attributen:", dir(sig))
    return None


def safeTimerCallback(timer, func):
    if hasattr(timer, "callback"):
        try:
            timer.callback.append(func)
            return None
        except Exception as e:
            print("[TheWeather] safeTimerCallback: .callback.append faalde:", e)
    return safeSignalConnect(timer.timeout, func)


def main(session, **kwargs):
    try:
        if not os.path.exists(CFG_DIR):
            os.makedirs(CFG_DIR)
            print("[TheWeather] Folder created successfully: %s" % CFG_DIR)
    except OSError as e:
        print("[TheWeather] Failed to create folder: %s" % str(e))

    global icoonpath, backgroundpath, _restartInProgress
    _restartInProgress = False
    
    if checkInternet():
        global SavedLokaleWeer
        SavedLokaleWeer = []
        locdirsave = CFG_DIR + "/TheWeather.cfg"
        if os.path.exists(locdirsave):
            for line in open(locdirsave):
                location = line.rstrip()
                SavedLokaleWeer.append(location)

        locdirsave = CFG_DIR + "/iconpack.cfg"
        if os.path.exists(locdirsave):
            for line in open(locdirsave):
                icoonpath = line.rstrip()

        locdirsave = CFG_DIR + "/TheWeather_bg.cfg"
        if os.path.exists(locdirsave):
            with open(locdirsave) as f:
                val = f.read().strip()
                if val and os.path.exists(val):
                    backgroundpath = val

        location = None
        locdirsave = CFG_DIR + "/TheWeather_last.cfg"
        if os.path.exists(locdirsave):
            for line in open(locdirsave):
                location = line.rstrip()

        if location and getLocWeer(location):
            time.sleep(1)
            session.open(sevendays)
        else:
            session.open(localcityscreen)

    else:
        session.open(MessageBox, _("Whoops!\nSlow or no Internet connection\nPlease try again"), MessageBox.TYPE_INFO)


def Plugins(path, **kwargs):
    return PluginDescriptor(name="TheWeather", description="WeatherInfo",
                            icon="Images/weerinfo.png",
                            where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)
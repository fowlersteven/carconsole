from machine     import Pin, PWM
import utime
import uasyncio

# global flags to ensure spaghetti code requirements met
cflag = False
dflag = False
eflag = False
fflag = False
gflag = False

# set up a Knob class to handle each of the pushbutton / rotary encoders
class Knob:
    def __init__(self, l_pin, r_pin, outpin, frq, dutycycle, name):

        # setup pins
        self.l_pin = Pin(l_pin, Pin.IN, Pin.PULL_DOWN)
        self.l_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.inputHandler)
        self.r_pin = Pin(r_pin, Pin.IN, Pin.PULL_DOWN)
        self.outpin = PWM(Pin(outpin))
        self.outpin.freq(frq)
        self.outpin.duty_u16(dutycycle)
        self.frq = frq
        self.max_freq = frq+7
        self.min_freq = frq-7
        self.temp_frq = frq
        self.name = name
        
        self.flag = self.l_pin.value()
        self.flag2 = self.r_pin.value()
        self.dir = 0
        
        self.timeoutms = 2500
        self.last_change = utime.ticks_ms()

        
    def adjustFrq(self, amt):
        if (self.temp_frq >= self.min_freq) & (self.temp_frq <= self.max_freq):
            self.temp_frq = self.temp_frq + amt
            self.outpin.freq(self.temp_frq)
            
        else:
            self.temp_frq = self.temp_frq - amt
            
        print (self.outpin.freq())

    def inputHandler(self, p):
        
        
        self.l_pin.irq(handler=None)
        
        utime.sleep_us(150)
        
        if not self.r_pin.value():
            self.dir = 1
        else:
            self.dir = -1
        
        
        utime.sleep_ms(1)
        
        
        
        self.l_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.inputHandler)
        
        
        
        
        
        
        
    def resetFlag(self):
        self.flag = self.l_pin.value()
        self.flag2 = self.r_pin.value()
        self.dir = 0
        
    def getDir(self):
        
        return self.dir
    
    
        
            
    
    

# Setup frequencies for notes and PWM signal Duty
duty = [
    3571,
    3231,
    2811,
    3111,
    2911
]

freqs = {
    "C":        131,
    "D":        147,
    "E":        165,
    "F":        175,
    "G":        196
    }

# instantiate all the Knobs inside a list
knobs = []

g = Knob(28,   26,  11,   freqs["G"],  duty[0], 'g')
f = Knob(14,   12,  13,   freqs["F"],  duty[1], 'f')
e = Knob(10,   9,   15,   freqs["E"],  duty[2], 'e')
d = Knob(8,    7,   4,   freqs["D"],  duty[3], 'd')
c = Knob(6,    5,   0,   freqs["C"],  duty[4], 'c')

knobs.append(c)
knobs.append(d)
knobs.append(e)
knobs.append(f)
knobs.append(g)

# define the 3.3V pin and blinking pin for relay
STEADY_ON = 3
BLINKER = 2

# time for blinking lights in ms
SLEEPMS = 400

# set the pins as in/output
relay_power = Pin(STEADY_ON,    mode=Pin.OUT,   value=1)
relay_ctrl  = Pin(BLINKER,      mode=Pin.OUT)

async def blinkerOn():
    while True:
        relay_ctrl.value(1)
        await uasyncio.sleep_ms(SLEEPMS)
        relay_ctrl.value(0)
        await uasyncio.sleep_ms(SLEEPMS)
        print('blink')

async def gradualReset(knob):
    
    if knob.frq > knob.temp_frq:
        for j in range(knob.temp_frq, knob.frq):
            knob.outpin.freq(j)
            print (knob.outpin.freq())
            await uasyncio.sleep_ms(190)
    if knob.temp_frq > knob.frq:
        for j in range(knob.frq, knob.temp_frq):
            knob.outpin.freq(knob.frq + knob.temp_frq - j-1)
            print (knob.outpin.freq())
            await uasyncio.sleep_ms(100)
    knob.outpin.freq(knob.frq)
    knob.temp_frq = knob.outpin.freq()


async def main():
    uasyncio.create_task(blinkerOn())
    while True:
        for i in knobs:
            
            a = i.getDir()
            if a is not 0:
                print(a)
                i.adjustFrq(a)
                i.last_change = utime.ticks_ms()
                
            if utime.ticks_ms() > i.last_change + i.timeoutms:
                i.last_change = utime.ticks_ms()
                uasyncio.create_task(gradualReset(i))
            
                
                
            
            
            
            i.resetFlag()
            #utime.sleep_ms(4)
            
            await uasyncio.sleep_ms(0)
        #for i in knobs:
            #i.resetFlag()
        

uasyncio.run(main())


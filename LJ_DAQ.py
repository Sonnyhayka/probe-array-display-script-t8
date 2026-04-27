from labjack import ljm

class LJMport:
    def __init__(self, name, _range=-1, _res=-1, _settling=-1, _neg=-1):      
        self.name = name 
        
        self.handle = ljm.openS("T8", "USB", "480010850")
    
        if(_range != -1):
            self.range = _range
            ljm.eWriteName(self.handle, self.name+'_RANGE', self.range)
        if(_res != -1):
            self.res = _res
            ljm.eWriteName(self.handle, self.name+'_RESOLUTION_INDEX', self.res)
        if(_settling != -1):
            self.settling = _settling
            ljm.eWriteName(self.handle, self.name+'_SETTLING_US', self.settling)
        if(_neg != -1):
            self.neg = _neg
            ljm.eWriteName(self.handle, self.name+'_NEGATIVE_CH', self.neg)
        self.value = 0

    @staticmethod
    def get(name):
        tmp = LJMport(name)
        result = tmp.read()
        return result

    @staticmethod
    def set(name, value):
        tmp = LJMport(name)
        tmp.write(value)
            
    def write(self, value):
        self.value = value
        ljm.eWriteName(self.handle, self.name, value)

    
    def writeFloat(self, value):
        self.value = value
        ljm.eWriteAddress(self.handle,self.name,ljm.constants.FLOAT32,value)

    def read(self):
        self.value = ljm.eReadName(self.handle, self.name)
        return self.value
    
if __name__ == '__main__':
    print("pressure")
    print(LJMport.get('AIN48'))

    LJMport.set('AIN50_RESOLUTION_INDEX', 12)
    LJMport.set('AIN50_RANGE', 0.01)
    LJMport.set('AIN50_SETTLING_US', 50)
    LJMport.set('AIN50_NEGATIVE_CH', 58)
    
    LJMport.set('AIN58_RESOLUTION_INDEX', 12)
    LJMport.set('AIN58_RANGE', 0.01)
    LJMport.set('AIN58_SETTLING_US', 50)
    
    print(LJMport.get('AIN50'))
    print(LJMport.get('AIN58'))
   
    for i in range(1,50):
        import time
        print(ljm.tcVoltsToTemp(6002, LJMport.get('AIN50'), LJMport.get('TEMPERATURE_DEVICE_K'))-273.15)
        time.sleep(1)
    
    ljm.closeAll()

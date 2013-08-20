from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker('txftw', 'txftw.demo.service', 'Twisted FTW Plugin',
                            'txftw')
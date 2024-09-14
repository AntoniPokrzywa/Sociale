from django.db import models
from shapely.geometry import Polygon, Point
from django.contrib.auth.models import User
from django.utils import timezone

class Bike(models.Model):
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    code = models.IntegerField()
    is_available = models.BooleanField()
    last_taken_by = models.ForeignKey(User, on_delete=models.PROTECT)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    bike = models.ForeignKey(Bike, on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField(null=True,blank=True)
    is_completed = models.BooleanField(null=True)

    def start_rental(self):
        self.start_time = timezone.now()
        self.bike.is_available = False
        self.is_completed = False
        self.bike.last_taken_by = self.user
        self.bike.save()
        self.save()

    def end_rental(self,lat,lon):
        self.end_time = timezone.now()
        self.bike.is_available = True
        self.is_completed = True
        self.bike.lat = lat
        self.bike.lon = lon
        self.bike.save()
        self.save()

class Polygon(models.Model):
    name = models.CharField(max_length=100)
    #Polygon points stored as JSON list
    poly = models.JSONField()

    def __init__(self, coords):
        if type(coords) == tuple:
            self.poly = {"coords": coords}
            self.save()
        else:
            print("Invalid Type")
        
    def contains_point(self, lat, lon):
        #((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
        if self.poly:
            polygon = Polygon(self.poly["coords"])
            point = Point(lat,lon)
            return polygon.contains_point(point)
        else:
            return False


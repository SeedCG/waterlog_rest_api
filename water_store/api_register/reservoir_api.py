__author__ = 'anthonymendoza'

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.apps import apps
from django.db.models import Q
from helpers.swp_reservoir_scraper import aggregate_scraped_data
from water_store.serializer_register import ReservoirSerializer
from water_store.serializer_register import ReclamationPlantSerializer, StreamSerializer, PrecipitationSerializer, \
    SpreadingGroundSerializer, EvapotranspirationSerializer
from datetime import datetime

reservoir_model = apps.get_model('water_store', 'Reservoir')


@api_view(['GET'])
def reservoir_api(request, format=None, **kwargs):
    if request.method == 'GET':
        query_filter = request.query_params['id']
        try:
            reservoirs = reservoir_model.objects.filter(dam_id__iexact=query_filter)
            if reservoirs.count() < 199:
                data = aggregate_scraped_data()
                for i in data.values():
                    for j in i:
                        if j['date'] is not None:
                            input_model = reservoir_model(dam_id=str(j['id']),
                                                          name=str(j['name']),
                                                          reservoir_elevation=None if j['reservoir elevation'] is None or j['reservoir elevation']=='--' else float(''.join(y for y in j['reservoir elevation'] if y.isdigit() or y == '.')),
                                                          reservoir_area=j['reservoir_area'] if type(j['reservoir_area']) is float else float(''.join(y for y in j['reservoir_area'] if y.isdigit() or y == '.')),
                                                          reservoir_storage=None if j['reservoir storage'] is None or j['reservoir storage']=='--' else float(''.join(y for y in j['reservoir storage'] if y.isdigit() or y == '.')),
                                                          latitude=j['latitude'],
                                                          longitude=j['longitude'],
                                                          county=str(j['county']),
                                                          stream=str(j['stream']),
                                                          storage_capacity=None if j['storage_capacity'] is None else float(''.join(y for y in j['storage_capacity'] if y.isdigit() or y == '.')),
                                                          outflow=None if j['outflow'] is None or j['outflow']=='--' else float(''.join(y for y in j['outflow'] if y.isdigit() or y == '.')),
                                                          inflow=None if j['inflow'] is None or j['inflow']=='--' else float(''.join(y for y in j['inflow'] if y.isdigit() or y == '.' or y == ',')),
                                                          precipitation_incremental=None if j['precipitation incremental'] is None or j['precipitation incremental']=='--'else float(''.join(y for y in j['precipitation incremental'] if y.isdigit() or y == '.')),
                                                          precipitation_accumulated=None if j['precipitation accumulated'] is None or j['precipitation accumulated']=='--'else float(''.join(y for y in j['precipitation accumulated'] if y.isdigit() or y == '.')),
                                                          date=datetime.strptime(j['date'], '%m/%d/%Y'),
                                                          source="State Water Project")
                            input_model.save()
                        else:
                            continue
            _serializer = ReservoirSerializer(reservoirs, many=True)
            return Response(_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise Response(e)
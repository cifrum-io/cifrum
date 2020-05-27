# swagger_client.RawValuesApi

All URIs are relative to *http://localhost:9000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**raw_values**](RawValuesApi.md#raw_values) | **GET** /raw-values/mut-ru/{registrationNumber} | Returns close values of a mutual fund by registrationNumber

# **raw_values**
> ModelsRawValues raw_values(registration_number, start_date, end_date)

Returns close values of a mutual fund by registrationNumber

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.RawValuesApi()
registration_number = 'registration_number_example' # str | 
start_date = '2013-10-20T19:20:30+01:00' # datetime | 
end_date = '2013-10-20T19:20:30+01:00' # datetime | 

try:
    # Returns close values of a mutual fund by registrationNumber
    api_response = api_instance.raw_values(registration_number, start_date, end_date)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RawValuesApi->raw_values: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **registration_number** | **str**|  | 
 **start_date** | **datetime**|  | 
 **end_date** | **datetime**|  | 

### Return type

[**ModelsRawValues**](ModelsRawValues.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


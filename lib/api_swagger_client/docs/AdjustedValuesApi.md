# swagger_client.AdjustedValuesApi

All URIs are relative to *http://localhost:9000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**adjusted_close_values**](AdjustedValuesApi.md#adjusted_close_values) | **GET** /adjusted-values/mut-ru/{registrationNumber} | Returns adjusted close values of a mutual fund by registrationNumber

# **adjusted_close_values**
> ModelsRawValues adjusted_close_values(registration_number, currency, start_date, end_date, period_frequency, interpolation_type)

Returns adjusted close values of a mutual fund by registrationNumber

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.AdjustedValuesApi()
registration_number = 'registration_number_example' # str | 
currency = 'currency_example' # str | 
start_date = 'start_date_example' # str | 
end_date = 'end_date_example' # str | 
period_frequency = 'period_frequency_example' # str | 
interpolation_type = 'interpolation_type_example' # str | 

try:
    # Returns adjusted close values of a mutual fund by registrationNumber
    api_response = api_instance.adjusted_close_values(registration_number, currency, start_date, end_date, period_frequency, interpolation_type)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AdjustedValuesApi->adjusted_close_values: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **registration_number** | **str**|  | 
 **currency** | **str**|  | 
 **start_date** | **str**|  | 
 **end_date** | **str**|  | 
 **period_frequency** | **str**|  | 
 **interpolation_type** | **str**|  | 

### Return type

[**ModelsRawValues**](ModelsRawValues.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


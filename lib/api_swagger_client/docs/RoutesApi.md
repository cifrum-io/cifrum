# swagger_client.RoutesApi

All URIs are relative to *http://localhost:9000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**message**](RoutesApi.md#message) | **GET** /api/message | A sample message that returns current time

# **message**
> ModelsMessage message()

A sample message that returns current time

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.RoutesApi()

try:
    # A sample message that returns current time
    api_response = api_instance.message()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RoutesApi->message: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ModelsMessage**](ModelsMessage.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


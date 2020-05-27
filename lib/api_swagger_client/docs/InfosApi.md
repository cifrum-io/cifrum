# swagger_client.InfosApi

All URIs are relative to *http://localhost:9000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mutru_info**](InfosApi.md#mutru_info) | **GET** /info/mut-ru/{registrationNumber} | Returns information of mutual fund by registrationNumber
[**mutru_infos**](InfosApi.md#mutru_infos) | **GET** /info/mut-ru/ | Returns all information of mutual funds

# **mutru_info**
> ModelsMutualFundRuInfo mutru_info(registration_number)

Returns information of mutual fund by registrationNumber

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.InfosApi()
registration_number = 'registration_number_example' # str | 

try:
    # Returns information of mutual fund by registrationNumber
    api_response = api_instance.mutru_info(registration_number)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling InfosApi->mutru_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **registration_number** | **str**|  | 

### Return type

[**ModelsMutualFundRuInfo**](ModelsMutualFundRuInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **mutru_infos**
> list[ModelsMutualFundRuInfo] mutru_infos()

Returns all information of mutual funds

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.InfosApi()

try:
    # Returns all information of mutual funds
    api_response = api_instance.mutru_infos()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling InfosApi->mutru_infos: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ModelsMutualFundRuInfo]**](ModelsMutualFundRuInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


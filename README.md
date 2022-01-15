# googled

Simple library for Google Drive in Python


### Setup
Currently available in Github
```python
pip install --upgrade git+https://github.com/thewh1teagle/googled
```

Examples can be found under [examples](https://github.com/thewh1teagle/googled/tree/main/examples) folder

##### You **must** retrive credentials.json for your Google drive API
<details>
  <summary>Instructions - Retrive credentials.json</summary>
  
  1. Go to https://console.cloud.google.com/
  2. Create new google project
  3. Name it, create it, choose it in dropdown on top
  4. Navigate to https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com
  5. enable it
  6. Navigate to https://console.cloud.google.com/apis/credentials/consent
  7. choose external, and create
  8. fill app name, user support mail, developer contact address, save and  continue
  9. select add or remove scopes, search google drive, select all, click right, select all again, click update in the bottom
  10. Save and continue
  11. select add users > fill your email, click add twice, save and continue
  12. click back to dashboard
  13. Navigate to https://console.cloud.google.com/apis/credentials/oauthclient
  14. Select Desktop app, name it, and create
  15. Click download json
  16. place it in the folder of your script
  17. That's all! Congrulations!
</details>



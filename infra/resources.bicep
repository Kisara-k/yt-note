// Resources bicep - deploys App Service Free F1 tier
param environmentName string
param location string
param principalId string
param resourceToken string

// App Service Plan (Free F1 tier)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'asp${resourceToken}'
  location: location
  sku: {
    name: 'F1'
    tier: 'Free'
    size: 'F1'
    family: 'F'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true // Required for Linux
  }
}

// Web App (API Service)
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: 'app${resourceToken}'
  location: location
  kind: 'app,linux'
  tags: {
    'azd-service-name': 'api'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: false // Not available in Free tier
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      pythonVersion: '3.11'
      appCommandLine: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000 --timeout 600'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'API_HOST'
          value: '0.0.0.0'
        }
        {
          name: 'API_PORT'
          value: '8000'
        }
        {
          name: 'API_RELOAD'
          value: 'false'
        }
      ]
    }
  }
}

// App Service Site Extension (required for deployment)
resource siteExtension 'Microsoft.Web/sites/siteextensions@2022-03-01' = {
  parent: webApp
  name: 'python'
}

// User Assigned Managed Identity (required by AZD)
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id${resourceToken}'
  location: location
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'logs${resourceToken}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi${resourceToken}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Outputs
output API_BASE_URL string = 'https://${webApp.properties.defaultHostName}'
output WEB_APP_NAME string = webApp.name
output MANAGED_IDENTITY_ID string = managedIdentity.id
output APP_INSIGHTS_CONNECTION_STRING string = appInsights.properties.ConnectionString

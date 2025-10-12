// Main bicep template for YouTube Notes Backend deployment
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used to generate resource names)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

// Generate resource group name
var resourceGroupName = 'rg-${environmentName}'

// Generate unique token for resource naming
var resourceToken = uniqueString(subscription().id, location, environmentName)

// Tags for Azure DevOps tracking
var tags = {
  'azd-env-name': environmentName
}

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// Deploy resources within the resource group
module resources './resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    environmentName: environmentName
    location: location
    principalId: principalId
    resourceToken: resourceToken
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP_ID string = rg.id
output RESOURCE_GROUP_ID string = rg.id
output API_BASE_URL string = resources.outputs.API_BASE_URL
output WEB_APP_NAME string = resources.outputs.WEB_APP_NAME

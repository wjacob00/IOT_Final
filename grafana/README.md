Current resource: https://grafana.com/tutorials/provision-dashboards-and-data-sources/#:~:text=Restart%20Grafana%20to%20provision%20the,grafyaml%20(YAML)

Folder to hold json files for:
  dashboard definition(s)
  
"In the provisioning/dashboards/ directory, create a file called default.yaml with the following content:"

YAML Copy

apiVersion: 1

providers:
  - name: Default # A uniquely identifiable name for the provider
    folder: Services # The folder where to place the dashboards
    type: file
    options:
      path:
        <path to dashboard definitions>
        # Default path for Windows: C:/Program Files/GrafanaLabs/grafana/public/dashboards
        # Default path for Linux is: /var/lib/grafana/dashboards


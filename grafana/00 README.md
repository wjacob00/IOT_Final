Current resource: https://grafana.com/tutorials/provision-dashboards-and-data-sources/#:~:text=Restart%20Grafana%20to%20provision%20the,grafyaml%20(YAML)

.
├── docker-compose.yml
└── provisioning
    └── dashboards
        ├── my-dashboard.json
        └── dashboard.yml

Folder to hold json files for:
    default.yaml to inform Grafana to search for jsons and where
    JSON definitions of dashboard
    
The rasperry PI OS on a virtual machine grafana created a folder here:
    /etc/grafana/provisioning/dashboards
    And included a sample.yaml 
/etc/grafana/provisioning shows all the general folders    




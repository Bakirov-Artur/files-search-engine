# Backup Files
Backup and archive files

## Install & Using
1. Cloned: http://gitlab.moex.com/spectra-devops/jenkins_backup.git
2. cd jenkins_backup
3. Create dir: mkdir etc
4. Create file: echo > etc/jenkins_backup.conf
5. Insert in file etc/jenkins_backup.conf:
```json
{
    "dump":{
        "name":"jenkins",
        "path":"/opt/",
        "type":"tar.gz",
        "items":[
            {
                "path":"/var/lib/jenkins/",
                "items":[
                    "users",
                    "nodes",
                    "*.xml",
                    "email-templates/*.jelly",
                    "plugins/*.hpi",
                    "plugins/*.jpi",
                    "plugins/.*\\w+.jpi.pinned",
                    "plugins/.*\\w+.hpi.pinned",
                    "secrets",
                    "nextBuildNumber",
                    ".ssh"
                ],
                "depth":3,
                "recursive":true
            },
            {
                "path": "/etc/nginx",
                "depth":3,
                "recursive":true
            }
        ]
    }
}
```
6. Add crontab task: crontab -e
```
*/15 * * * * /usr/bin/python /your/path/to/jenkins_backup/dump.py >/dev/null 2>&1
```

## License
This project is licensed under the MIT License

##Author
Send any other comments, patches, flowers and suggestions to [Bakirov Artur](mailto:turkin86@mail.ru)

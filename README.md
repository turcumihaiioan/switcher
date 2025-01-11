<p align="center">
  <img src="assets/logo.svg" width="20%">
  <br>
  <em>switcher is a web interface and REST API for easy task automation.</em>
</p>

---

## Installing switcher

### Build a container image using a Containerfile

```bash
podman build --tag switcher .
```
### Run the container

```bash
podman container run --detach --env-file .env --name switcher --publish 8000:8000 localhost/switcher:latest
```

## License

switcher is licensed under the [GNU General Public License v3.0 or later](LICENSE)

switcher logo by Turcu Mihai Ioan is licensed under the [Creative Commons Attribution 4.0 International](LICENSE-LOGO)

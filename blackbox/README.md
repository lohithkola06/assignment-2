# Blackbox Testing

## Start QuickCart

On Apple Silicon / ARM64 machines:

```bash
docker load -i quickcart_image.tar
docker run --rm --name quickcart-blackbox -p 8080:8080 quickcart:latest
```

On x86_64 machines:

```bash
docker load -i quickcart_image_x86.tar
docker run --rm --name quickcart-blackbox -p 8080:8080 quickcart:latest
```

## Run the Tests

```bash
python3 -m pytest blackbox/tests -v
```

Optional environment variables:

- `QUICKCART_BASE_URL` defaults to `http://127.0.0.1:8080`
- `ROLL_NUMBER` defaults to `23110001`

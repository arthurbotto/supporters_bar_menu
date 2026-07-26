# Archived: original EC2 deploy workflow

This is the deploy workflow used when the app was hosted on AWS EC2 (Amazon Linux,
Flask in a single Docker container, separate RDS Postgres). Superseded on migration
to Hetzner (Docker Compose, Postgres container, git-pull deploy over SSH).

Kept for reference only. This is NOT an active workflow (the .md extension means
GitHub Actions ignores it).

```yaml
name: Deploy to EC2

on:
  push:
    branches: [main]

jobs:
  test:
    uses: ./.github/workflows/ci.yml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: prod

    steps:
      - uses: actions/checkout@v4

      - name: Copy app to EC2
        uses: appleboy/scp-action@v0.1.4
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ec2-user
          port: 22
          key: ${{ secrets.EC2_SSH_KEY }}
          source: "."
          target: ~/bar-menu

      - name: Build and run on EC2
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ec2-user
          port: 22
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd ~/bar-menu
            docker build -t bar-menu:latest .
            docker stop bar-menu || true
            docker rm bar-menu || true
            docker image prune -f || true
            docker run -d \
              --name bar-menu \
              --restart unless-stopped \
              -p 5001:5001 \
              -v /home/ec2-user/bar-menu-images/wine:/app/static/images/wine \
              -v /home/ec2-user/bar-menu-images/cocktails:/app/static/images/cocktails \
              -e DATABASE_URL='${{ secrets.DATABASE_URL }}' \
              -e SECRET_KEY='${{ secrets.SECRET_KEY }}' \
              -e ADMIN_USERNAME='${{ secrets.ADMIN_USERNAME }}' \
              -e ADMIN_PASSWORD_HASH='${{ secrets.ADMIN_PASSWORD_HASH }}' \
              -e APP_ENV=production \
              bar-menu:latest```

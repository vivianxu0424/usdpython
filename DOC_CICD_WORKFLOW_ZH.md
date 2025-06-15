# GitHub + AWS SAM CI/CD 设计文档

本文档描述如何在本项目中通过 GitHub Actions 与 AWS SAM 搭建持续集成、持续部署(CI/CD)流程，使代码合并到 `main` 分支后可以自动部署到 AWS Lambda 或其他 AWS 服务。

## 总体流程
1. **触发条件**：当 Pull Request 被合并到 `main` 分支时，GitHub Actions 工作流被触发。
2. **依赖安装与测试**：工作流首先安装项目依赖，并执行 `pytest` 保证所有测试通过。
3. **构建与打包**：使用 AWS SAM 对应用进行打包，生成部署所需的模板和构件。
4. **部署到 AWS**：借助 `aws-actions/configure-aws-credentials` 配置凭证后，执行 `sam deploy` 将新的 Lambda 函数或其他资源部署到指定的 AWS 账户与 Region。

## GitHub Actions 工作流示例
下面示例说明主要步骤，具体内容可根据项目需要调整：
```yaml
name: Deploy with SAM

on:
  push:
    branches: [main]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install usd-core numpy pytest aws-sam-cli
      - name: Run tests
        run: pytest
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-1
      - name: Build and deploy with SAM
        run: |
          sam build
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

## 权限与安全性
- 推荐将 AWS 凭证存储在 GitHub `Secrets` 中，并赋予最小化的 IAM 权限，仅允许部署所需资源。
- 可使用 `sam deploy --guided` 预先生成配置文件，如 `samconfig.toml`，在流水线中复用。

## 其他注意事项
- 如需部署到非 Lambda 的服务(例如 ECS、API Gateway 等)，可在 `template.yaml` 中定义相应资源，SAM 将统一管理。
- 在生产环境前建议再添加一个手动批准步骤，或采用多环境策略(如 `dev`, `staging`, `prod`) 以降低风险。
- 工作流运行日志可在 GitHub Actions 页查看，便于追踪每次部署的结果。


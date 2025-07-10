<h1 align="center">
  <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBkPSJNMTIgLjI5N2MtNi42MyAwLTEyIDUuMzczLTEyIDEyIDAgNS4zMDMgMy40MzggOS44IDguMjA1IDExLjM4NS42LjExMy44Mi0uMjU4LjgyLS41NzcgMC0uMjg1LS4wMS0xLjA0LS4wMTUtMi4wNC0zLjMzOC43MjQtNC4wNDItMS42MS00LjA0Mi0xLjYxLS41NDYtMS4zODctMS4zMzUtMS43NTYtMS4zMzUtMS43NTYtMS4wOS0uNzQ0LjA4Mi0uNzI5LjA4Mi0uNzI5IDEuMjA1LjA4NCAxLjgzOCAxLjIzNiAxLjgzOCAxLjIzNiAxLjA3IDEuODI2IDIuODAyIDEuMjk5IDMuNDg1Ljk5NC4xMDgtLjc3Mi40MTctMS4zLjc2LTEuNjA1LTIuNjY1LS4zLTUuNDY2LTEuMzMyLTUuNDY2LTUuOTMgMC0xLjMxLjQ2NS0yLjM4IDEuMjM1LTMuMjItLjEyNS0uMy0uNTM1LTEuNTI0LjE١NS0zLjE3NiAwIDAgMS4wMDUtLjMyMiAzLjMgMS4yMy45Ni0uMjY3IDEuOTgtLjQgMi45OS0uNDA0IDEuMDEuMDA0IDIuMDMuMTM3IDIuOTkuNDA0IDIuMjg1LTEuNTUyIDMuMjk1LTEuMjMgMy4yOTUtMS4yMy42OSAxLjY1Mi4yOCAyLjg3Ni4xNTUgMy4xNzYuNzcuODQgMS4yMzUgMS45MSAxLjIzNSAzLjIyIDAgNC42MTYtMi44MDUgNS42MjQtNS40NzUgNS45Mi40My4zNy44MiAxLjA5Ni44MiAyLjIyIDAgMS42MDYtLjAxNSAyLjg5Ni0uMDE1IDMuMjg2IDAgLjMxNS4yMS42OS44MjUuNTdDDIwLjU2NSA٢Mi4wOTcgMjQgMTcuNTk3IDI0IDEyLjI5N2MyNC02LjYyNy01LjM3My0xMi0xMi0xMnoiLz48L3N2Zz4=" alt="GitHub Logo" width="120" style="vertical-align:middle; filter: invert(1);">
  Proactive Security and Compliance Assistant
</h1>
<h3 align="center">(Proaktif Güvenlik ve Uyumluluk Asistanı)</h3>

This GitHub Action proactively scans your codebase for security vulnerabilities and compliance issues. It aims to "shift-left" security by integrating checks early in the development lifecycle, identifying and fixing problems before they reach production.

Bu GitHub Action, kod tabanınızı güvenlik açıkları ve uyumluluk sorunları için proaktif olarak tarar. Geliştirme yaşam döngüsünün başlarında kontrolleri entegre ederek, sorunları üretime ulaşmadan önce tespit edip düzeltmeyi amaçlar.

---

## Features (Özellikler)

-   **Sensitive Data Leakage Detection**: Scans the code for API keys, private keys, and other secrets accidentally committed, using advanced regex patterns.
    -   **Hassas Veri Sızıntısı Tespiti**: Koda yanlışlıkla eklenmiş API anahtarları, özel anahtarlar ve diğer gizli bilgileri gelişmiş regex desenleri kullanarak tarar.
-   **License Compliance Auditing**: Compares your project's dependency licenses against a configurable allowlist and reports any non-compliant licenses.
    -   **Lisans Uyumluluğu Denetimi**: Projenizin bağımlılık lisanslarını yapılandırılabilir bir izin verilenler listesiyle karşılaştırır ve uyumlu olmayan lisansları raporlar.
-   **IaC (Infrastructure as Code) Security Scanning**: Detects common cloud security misconfigurations in Terraform and CloudFormation files using `checkov`.
    -   **Altyapı Kodu (IaC) Güvenlik Taraması**: `checkov` kullanarak Terraform ve CloudFormation dosyalarındaki yaygın bulut güvenlik yapılandırma hatalarını tespit eder.
-   **Dangerous Function Usage Warnings**: Identifies the use of potentially unsafe functions like `eval()` or `dangerouslySetInnerHTML` that require manual review.
    -   **Tehlikeli Fonksiyon Kullanımı Uyarıları**: `eval()` veya `dangerouslySetInnerHTML` gibi manuel inceleme gerektiren potansiyel olarak güvenli olmayan fonksiyonların kullanımını belirler.

---

## How It Works (Nasıl Çalışır?)

This Action is triggered on every `push` or `pull_request`. It scans the codebase based on a specified configuration file and can block PRs or fail the build process based on its findings.

Bu Action, her `push` veya `pull_request` işleminde tetiklenir. Belirtilen bir yapılandırma dosyasına göre kod tabanını tarar ve bulgularına dayanarak Pull Request'leri engelleyebilir veya build sürecini başarısız kılabilir.

---

## Usage (Kullanım)

### 1. Create Workflow File (Workflow Dosyası Oluşturun)

Add a workflow file to your repository, for example, at `.github/workflows/security_check.yml`:
Deponuza `.github/workflows/security_check.yml` gibi bir yolda bir workflow dosyası ekleyin:

```yaml
name: Proactive Security Scan
on: [push, pull_request]

jobs:
  security_scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # This step is required to scan Node.js dependencies.
      # Python dependencies from requirements.txt are installed automatically by the action.
      - name: Install NPM Dependencies
        if: hashFiles('**/package-lock.json') != ''
        run: npm install

      - name: Run Proactive Security Assistant
        # If you were to publish this action to the marketplace, you would use:
        # uses: your-username/proactive-security-assistant@v1
        # For local testing, we use the relative path:
        uses: ./proactive-security-assistant
        with:
          # The path to the repository to be scanned.
          repo_path: '.'
          # (Optional) The path to the configuration file.
          config_path: '.github/security-config.yml'
```

### 2. (Optional) Customize Configuration (Yapılandırmayı Özelleştirin)

You can customize the scanning rules by adding a `security-config.yml` file to your repository. You can place it in the root directory or, preferably, in the `.github/` directory.
Tarama kurallarını özelleştirmek için deponuza bir `security-config.yml` dosyası ekleyebilirsiniz. Bu dosyayı ana dizine veya tercihen `.github/` dizinine yerleştirebilirsiniz.

For a complete list of configurable rules, see the example [`config.yml`](config.yml) file in this action's repository.
Yapılandırılabilir kuralların tam listesi için bu action deposundaki örnek [`config.yml`](config.yml) dosyasına bakın.

---

## Contributing (Katkıda Bulunma)

Contributions are welcome! Please open an issue or submit a pull request.
Katkılarınızı bekliyoruz! Lütfen bir issue açın veya bir pull request gönderin.

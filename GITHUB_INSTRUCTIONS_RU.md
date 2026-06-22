# Как отправить проект преподавателю через GitHub

## Вариант 1 — самый простой: через сайт GitHub

1. Зайди на https://github.com и войди в аккаунт.
2. Нажми `+` в правом верхнем углу → `New repository`.
3. В поле `Repository name` напиши, например: `math-expression-calculator`.
4. Выбери `Public`, чтобы преподаватель мог открыть ссылку.
5. Не ставь галочки `Add a README`, `.gitignore`, `license`, потому что эти файлы уже есть в архиве.
6. Нажми `Create repository`.
7. На странице нового репозитория нажми `uploading an existing file`.
8. Распакуй архив `calculator-repo.zip` на компьютере.
9. Выдели все файлы и папки внутри распакованной папки `calculator-repo` и перетащи их в окно GitHub.
10. Внизу страницы нажми `Commit changes`.
11. Скопируй ссылку из адресной строки браузера и отправь преподавателю.

## Вариант 2 — через Git, если он установлен

```bash
cd calculator-repo
git init
git add .
git commit -m "Initial calculator implementation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/math-expression-calculator.git
git push -u origin main
```

В ссылке замени `YOUR_USERNAME` на свой логин GitHub.

## Что лучше отправить преподавателю

Отправь ссылку вида:

```text
https://github.com/YOUR_USERNAME/math-expression-calculator
```

После загрузки GitHub Actions запустятся автоматически. Если преподаватель откроет вкладку `Actions`, он увидит проверки lint, tests, security и build.

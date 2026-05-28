# Cursor Cloud Agent Skills API/Web 测试技术验证

本仓库是一套从零搭建的 Cursor Skills PoC，用来验证：通过编写 Cursor Skills，引导 Cursor IDE 的 Cloud Agent 自动生成并运行 API 测试与 Web UI 测试。

- API 测试栈：Python + pytest + requests
- API 演示对象：优衣库中国官网真实只读接口（从 `https://www.uniqlo.cn` 页面网络请求中探索得到）
- Web UI 测试栈：Playwright + TypeScript
- Web UI 演示对象：优衣库中国官网 (`https://www.uniqlo.cn`)
- 交付重点：`.cursor/skills/*/SKILL.md` 中的 Agent 指引，而不是测试代码本身

### 当前 API 测试目标

通过 Playwright 抓取 `www.uniqlo.cn` 首页和 `/c/3wtshirt.html` 分类页网络请求，确认可用于演示的接口包括：

- `GET https://d.uniqlo.cn/p/hmall-bd-service/recommendWord/getRecommendWord/zh_CN`
- `POST https://d.uniqlo.cn/p/hmall-sc-service/search/searchCategoryInfo/zh_CN`
- `POST https://d.uniqlo.cn/p/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN`
- `GET https://www.uniqlo.cn/data/shop_classification_PC.json`

这些接口无需登录，适合做 Cloud Agent demo。测试仍会保留 live-site skip 策略，因为公开商业站点可能对云环境限流、阻断或临时调整响应结构。

## 1. Cursor Skills 机制说明

Cursor Skill 是一个包含 `SKILL.md` 的目录，用来给 Agent 提供某类任务的专用上下文、约束和操作步骤。项目级 Skill 推荐放在：

```text
.cursor/skills/<skill-name>/SKILL.md
```

Cursor 会发现项目级和用户级 Skills，并根据用户请求、当前上下文、文件路径和 Skill 描述决定是否把 Skill 提供给 Agent。用户也可以在聊天中通过 `/skill-name` 显式调用。

### SKILL.md frontmatter

`SKILL.md` 顶部使用 YAML frontmatter：

```yaml
---
name: api-testing
description: Use this skill when creating Python API tests with pytest and requests.
paths:
  - "tests/api/**/*.py"
---
```

字段说明与最佳实践：

| 字段 | 作用 | 最佳实践 |
| --- | --- | --- |
| `name` | Skill 的唯一标识，通常也用于 `/skill-name` 调用 | 必填；使用小写字母、数字、连字符；与父目录名一致，例如 `.cursor/skills/api-testing/SKILL.md` 的 `name` 是 `api-testing` |
| `description` | 描述 Skill 适用场景，Agent 会用它判断是否相关 | 必填；写清“什么时候使用”和“解决什么任务”，比泛泛描述更容易被正确匹配 |
| `paths` | 新版 Cursor Skills 推荐的路径匹配字段，用 glob 限定 Skill 适用文件 | 对测试类 Skill，建议限定到测试目录和配置文件，例如 `tests/api/**/*.py`、`tests/web/**/*.ts` |
| `globs` | 旧版/兼容字段，也常见于 Cursor Rules | 新 Skill 优先使用 `paths`；如果团队仍使用旧 Rules，可在迁移说明里解释，但不建议新写 Skill 依赖 `globs` |
| `alwaysApply` | Cursor Rules 的字段，表示规则总是应用 | 不建议放在 Skill 中；Skills 更适合让 Agent 按描述和上下文决定是否应用，或由用户通过 `/skill-name` 显式触发 |
| `disable-model-invocation` | 禁止 Agent 自动调用，只允许用户显式 `/skill-name` 调用 | 适合命令式模板或危险操作；本 PoC 需要验证自动引导能力，所以未使用 |
| `metadata` | 附加元数据 | 可用于团队分类、版本等，不应承载核心指令 |

### Agent 如何匹配和使用 Skill

1. Cursor 扫描 `.cursor/skills/`、`.agents/skills/` 以及用户级 Skills 目录。
2. 每个包含 `SKILL.md` 的目录被识别为一个 Skill。
3. Agent 根据用户 prompt、当前打开/修改的文件、`description` 和 `paths` 判断是否需要使用 Skill。
4. 如果用户在聊天里显式输入 `/api-testing` 或 `/web-ui-testing`，Agent 会优先加载对应 Skill。
5. Agent 读取 Skill 正文后，按其中的项目结构、命名规范、断言模式、运行命令和检查清单执行任务。

### 编写 Skills 的建议

- `description` 要具体，例如“当创建 `tests/web/**/*.ts` 的 Playwright 测试时使用”。
- Skill 正文保持任务导向：目录约定、命名规范、示例、运行命令、检查清单。
- 大量背景资料可拆到 `references/`，脚本可放到 `scripts/`；本 PoC 为了便于演示，全部说明集中在 `SKILL.md`。
- 不要把 Skill 写成宽泛文档；它应该能直接改变 Agent 生成代码的风格和质量。
- 对 live API/live website 测试，要明确网络失败、限流、反爬、弹窗等环境问题如何处理。

## 2. 完整项目结构

```text
.
├── .cursor/
│   └── skills/
│       ├── api-testing/
│       │   └── SKILL.md
│       └── web-ui-testing/
│           └── SKILL.md
├── tests/
│   ├── api/
│   │   ├── conftest.py
│   │   ├── test_uniqlo_category_search.py
│   │   └── test_uniqlo_site_data.py
│   └── web/
│       ├── navigation.spec.ts
│       ├── search.spec.ts
│       └── uniqlo.helpers.ts
├── .gitignore
├── package.json
├── playwright.config.ts
├── pytest.ini
├── README.md
├── requirements.txt
└── tsconfig.json
```

### 文件用途

| 文件 | 用途 |
| --- | --- |
| `.cursor/skills/api-testing/SKILL.md` | API 测试 Skill，指导 Agent 用 pytest + requests 生成结构化 API 测试 |
| `.cursor/skills/web-ui-testing/SKILL.md` | Web UI 测试 Skill，指导 Agent 用 Playwright + TypeScript 生成优衣库中文站 E2E 测试 |
| `requirements.txt` | Python API 测试依赖：pytest、requests |
| `pytest.ini` | pytest 发现规则、严格 marker、API 测试目录配置 |
| `tests/api/conftest.py` | API 测试共享 fixtures：优衣库 API/web base URL、requests session、请求失败 skip、JSON/Hmall envelope 断言 |
| `tests/api/test_uniqlo_category_search.py` | 优衣库 `hmall-sc-service` 分类元数据与商品列表接口演示测试 |
| `tests/api/test_uniqlo_site_data.py` | 优衣库推荐词接口与 PC 分类 JSON 资源演示测试 |
| `package.json` | Node 项目与 Playwright 测试脚本 |
| `tsconfig.json` | TypeScript 编译/类型检查配置 |
| `playwright.config.ts` | Playwright 配置：Chromium、中文 locale、上海时区、trace/screenshot/video |
| `tests/web/uniqlo.helpers.ts` | 优衣库中文站通用 helper：打开首页、处理弹窗、搜索、反爬 skip |
| `tests/web/search.spec.ts` | 搜索流程演示测试 |
| `tests/web/navigation.spec.ts` | 顶部导航/分类浏览演示测试 |
| `.gitignore` | 忽略虚拟环境、node_modules、Playwright 报告等生成物 |

## 3. Skills 文件

完整 Skill 内容位于：

- `.cursor/skills/api-testing/SKILL.md`
- `.cursor/skills/web-ui-testing/SKILL.md`

这两个文件分别包含：项目结构约定、命名规范、断言模式、公共 API/live 网站处理方式、示例代码、运行命令和 Agent 生成检查清单。

## 4. 演示测试代码

API 演示测试：

- `tests/api/test_uniqlo_category_search.py`
- `tests/api/test_uniqlo_site_data.py`

Web UI 演示测试：

- `tests/web/search.spec.ts`
- `tests/web/navigation.spec.ts`
- `tests/web/uniqlo.helpers.ts`

这些测试的设计目标是证明 Agent 在 Skill 引导下会生成：

- 稳定目录结构
- 可复用 fixtures/helpers
- 清晰命名
- 分层断言
- 对 live service 环境问题的合理 skip
- 中文电商网站下的弹窗、locale、反爬和选择器策略处理

## 5. 本地运行方式

### API 测试

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/api -q
```

### Web UI 测试

```bash
npm install
npx playwright install chromium
npm run test:web
```

如果 cloud runner 被优衣库官网反爬或限流，Web 测试会以明确原因 skip；如果页面正常加载，测试会继续执行真实断言。

API 测试也访问优衣库 live endpoints。如果接口返回 403、429、5xx 或网络不可达，测试 helper 会将其标记为环境 skip；如果接口正常返回 JSON，则会执行真实的 schema、类型和业务语义断言。

## 6. Cursor Cloud Agent 演示流程

### Skills 怎么运行/触发

Cursor Skill 不是一个需要手动执行的脚本，而是一份给 Agent 读取的任务说明。运行方式有两种：

1. **显式触发**：在 Cursor Agent Chat 里输入 `/api-testing` 或 `/web-ui-testing`，然后继续写你的需求。这样 Agent 会明确加载对应 Skill。
2. **自动匹配**：直接让 Agent 修改 `tests/api/**/*.py` 或 `tests/web/**/*.ts`，Cursor 会根据 `SKILL.md` 的 `description` 和 `paths` 判断是否把相关 Skill 提供给 Agent。

Skill 被触发后，Agent 会根据 `SKILL.md` 中的约定去写代码、复用 helper、选择测试命令并运行验证。真正被运行的是测试命令，例如：

```bash
python3 -m pytest tests/api -q
npm run test:web
```

### 步骤 A：确认 Skill 可被发现

1. 在 Cursor 打开本仓库。
2. 确认目录存在：
   - `.cursor/skills/api-testing/SKILL.md`
   - `.cursor/skills/web-ui-testing/SKILL.md`
3. 在 Agent Chat 输入 `/`，检查是否能搜索到 `api-testing` 和 `web-ui-testing`。
4. 也可以不显式调用，让 Agent 根据 `description` 和 `paths` 自动匹配。

### 步骤 B：触发 API 测试生成和运行

推荐 prompt：

```text
/api-testing
请基于当前仓库的 API 测试约定，为优衣库中国官网的 hmall-sc-service 新增一个 pytest + requests 测试。
要求：放在 tests/api/test_uniqlo_product_listing.py；复用 conftest.py 里的 fixtures；使用 searchWithCategoryCodeAndConditions/zh_CN 查询 3wtshirt 分类；断言 success、resp 分段、筛选项、商品 code/name/price/stock 字段；最后运行 python3 -m pytest tests/api -q。
```

也可以测试自动匹配：

```text
请在 tests/api 下新增一个优衣库中国官网推荐词 API 测试，遵循本仓库 API 测试风格，并运行 API 测试。
```

预期 Agent 行为：

1. 读取 `api-testing` Skill。
2. 使用 `api_client`、`api_base_url`、`uniqlo_web_base_url`、`request_or_skip`、`assert_json_response`、`assert_hmall_success`。
3. 生成 `tests/api/test_uniqlo_<resource>.py`。
4. 运行 `python3 -m pytest tests/api -q`。
5. 汇报 pass/skip/fail。

### 步骤 C：触发 Web UI 测试生成和运行

推荐 prompt：

```text
/web-ui-testing
请基于当前仓库的 Playwright 约定，为优衣库中国官网新增一个商品分类浏览测试。
要求：放在 tests/web/category-browse.spec.ts；复用 uniqlo.helpers.ts；优先使用中文可访问名称定位；处理弹窗和反爬 skip；断言页面出现商品、分类或系列相关内容；最后运行 npm run test:web。
```

也可以测试自动匹配：

```text
请在 tests/web 下新增一个优衣库中国官网搜索“羽绒服”的 Playwright 测试，遵循本仓库 Web UI 测试风格，并运行 Web 测试。
```

预期 Agent 行为：

1. 读取 `web-ui-testing` Skill。
2. 复用 `gotoUniqloHome`、`dismissKnownOverlays`、`searchUniqlo`、`skipIfBlockedOrChallenged`。
3. 使用中文 label/placeholder 优先的 locator 策略。
4. 生成 `*.spec.ts`。
5. 运行 `npm run test:web`。
6. 如果 live site 阻止 cloud runner，报告 skip 原因；否则报告真实断言结果。

### 步骤 D：验收点

- Agent 生成的新测试是否放在约定目录。
- 是否复用 fixtures/helpers，而不是复制粘贴大量请求或弹窗逻辑。
- API 测试是否包含状态码、content-type、schema/type、业务语义断言。
- Web 测试是否优先使用可访问 selector，并处理中文站弹窗/反爬/locale。
- Agent 是否自动运行对应测试命令并报告结果。
- 当 live 依赖不可达时，是否清楚区分环境 skip 与真实测试失败。

# RenderData抽象层架构设计

## 1. 设计背景

在原有的渲染架构中，数据处理与视图渲染紧密耦合，导致代码难以扩展和维护。当需要添加新的平台支持时，需要修改大量现有代码，增加了引入bug的风险。为了解决这个问题，我们设计了RenderData抽象层，将数据处理与视图渲染解耦，提升了系统的扩展性和可维护性。

## 2. 核心设计思路

### 2.1 抽象接口设计

我们设计了`RenderData`抽象接口，定义了统一的数据结构和访问方法，使不同平台的渲染数据可以通过统一的接口进行访问。`RenderData`接口包含以下核心方法：

- `get_description()`: 获取文章描述
- `get_article_content()`: 获取处理后的文章内容
- `get_public_data()`: 获取公共渲染数据
- `get_post_type()`: 获取文章类型
- `process()`: 处理数据的主方法

### 2.2 分层架构

新的渲染架构采用了分层设计：

1. **抽象层**：`RenderData`接口定义了统一的数据访问方式
2. **实现层**：不同平台实现自己的`RenderData`子类，如`HyperionRenderData`和`HoyolabRenderData`
3. **渲染层**：使用统一的接口访问数据，进行视图渲染

### 2.3 数据处理流程

1. 获取原始文章信息
2. 根据平台类型创建对应的`RenderData`实例
3. 调用`RenderData`实例的方法获取处理后的数据
4. 使用模板渲染视图

## 3. 实现细节

### 3.1 RenderData抽象类

```python
class RenderData(ABC):
    def __init__(self, post_info: PostInfo):
        self._post_info = post_info
        self._processed_data = {}
    
    @property
    def post_info(self) -> PostInfo:
        return self._post_info
    
    @property
    def processed_data(self) -> Dict[str, Any]:
        return self._processed_data
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_article_content(self) -> str:
        pass
    
    @abstractmethod
    def get_public_data(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_post_type(self) -> PostType:
        pass
    
    def process(self) -> None:
        pass
```

### 3.2 基础实现

我们提供了`BaseRenderData`基础实现，包含了通用的功能，如获取文章类型：

```python
class BaseRenderData(RenderData):
    def __init__(self, post_info: PostInfo, i18n):
        super().__init__(post_info)
        self._i18n = i18n
    
    def get_post_type(self) -> PostType:
        return self._post_info.view_type
```

### 3.3 平台特定实现

不同平台可以继承`BaseRenderData`，实现自己的特定逻辑：

```python
class HyperionRenderData(BaseRenderData):
    def __init__(self, post_info: PostInfo, i18n: I18n, related_posts_func: Callable):
        super().__init__(post_info, i18n)
        self._related_posts_func = related_posts_func
    
    def get_description(self) -> str:
        # 平台特定的描述获取逻辑
        pass
    
    def get_article_content(self) -> str:
        # 平台特定的内容处理逻辑
        pass
    
    def get_public_data(self) -> Dict[str, Any]:
        # 平台特定的公共数据获取逻辑
        pass
```

## 4. 扩展方法

### 4.1 添加新平台支持

要添加新平台支持，只需：

1. 创建新的`RenderData`子类，继承`BaseRenderData`
2. 实现抽象方法，添加平台特定的处理逻辑
3. 在渲染入口处，根据平台类型创建对应的`RenderData`实例

### 4.2 扩展现有平台功能

要扩展现有平台的功能，只需修改对应的`RenderData`子类，无需修改渲染逻辑：

1. 在`RenderData`子类中添加新的处理方法
2. 在现有方法中调用新的处理方法
3. 如需修改数据结构，可以扩展`processed_data`字典

## 5. 代码结构

```
src/render/
├── __init__.py
├── article.py              # 米游社国内版渲染逻辑
├── article_hoyolab.py      # 米游社国际版渲染逻辑
└── render_data.py          # RenderData抽象层
```

## 6. 使用示例

### 6.1 创建RenderData实例

```python
# 创建RenderData实例
render_data = HyperionRenderData(post_info, i18n, get_recommend_post)

# 获取处理后的数据
description = render_data.get_description()
article_content = render_data.get_article_content()
public_data = render_data.get_public_data()

# 渲染模板
template.render(
    description=description,
    article=article_content,
    **public_data,
)
```

### 6.2 扩展新平台

```python
class NewPlatformRenderData(BaseRenderData):
    def get_description(self) -> str:
        # 新平台的描述获取逻辑
        return "新平台描述"
    
    def get_article_content(self) -> str:
        # 新平台的内容处理逻辑
        return "<p>新平台内容</p>"
    
    def get_public_data(self) -> Dict[str, Any]:
        # 新平台的公共数据获取逻辑
        return {
            "platform": "new_platform",
            # 其他公共数据
        }
```

## 7. 优势与收益

### 7.1 提升扩展性

新的架构使添加新平台支持变得更加容易，只需创建新的`RenderData`子类，无需修改现有渲染逻辑。

### 7.2 提升可维护性

数据处理与视图渲染解耦，使代码结构更加清晰，易于维护和调试。

### 7.3 统一接口

不同平台的数据通过统一的接口进行访问，使渲染逻辑更加简洁。

### 7.4 降低风险

修改现有平台功能时，只需修改对应的`RenderData`子类，不会影响其他平台的功能。

## 8. 未来规划

1. 进一步优化`RenderData`抽象层，添加更多通用功能
2. 支持更多平台的渲染需求
3. 增强数据处理的灵活性，支持自定义数据处理流程
4. 添加更多的单元测试，确保架构的稳定性

## 9. 总结

RenderData抽象层的设计成功地将数据处理与视图渲染解耦，提升了系统的扩展性和可维护性。新的架构支持米游社(hoyolab)平台的渲染需求，并预留了清晰的扩展接口，便于后续添加新平台支持。重构过程中保持了原有功能不变，通过单元测试验证了重构的正确性。
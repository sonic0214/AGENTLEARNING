"""
User-friendly error messages for different error categories.

Maps technical error categories to user-friendly messages with suggestions.
"""
from .result import ErrorCategory

# Error message templates for each category
ERROR_MESSAGES = {
    ErrorCategory.AGENT_EXECUTION: {
        "user": "分析代理执行时遇到问题,无法完成分析",
        "suggestion": "请重试一次,如果问题持续存在请联系技术支持"
    },
    ErrorCategory.PARSING: {
        "user": "收到分析数据但解析失败",
        "suggestion": "这通常是临时问题,请稍后重试"
    },
    ErrorCategory.CONFIGURATION: {
        "user": "系统配置错误",
        "suggestion": "请检查API密钥和系统配置是否正确"
    },
    ErrorCategory.EXTERNAL_API: {
        "user": "外部服务(如Google搜索)暂时不可用",
        "suggestion": "请稍等片刻后重试"
    },
    ErrorCategory.TIMEOUT: {
        "user": "分析耗时超过预期",
        "suggestion": "请尝试分析更具体的产品类别"
    },
    ErrorCategory.VALIDATION: {
        "user": "输入数据不符合要求",
        "suggestion": "请检查输入并重试"
    },
    ErrorCategory.RESOURCE: {
        "user": "系统资源暂时不可用",
        "suggestion": "请稍后重试"
    }
}


def get_error_message(category: ErrorCategory, include_suggestion: bool = True) -> str:
    """
    Get user-friendly error message for a category.

    Args:
        category: Error category
        include_suggestion: Whether to include suggestion text

    Returns:
        User-friendly error message

    Example:
        >>> get_error_message(ErrorCategory.PARSING)
        '收到分析数据但解析失败。这通常是临时问题,请稍后重试'
        >>> get_error_message(ErrorCategory.PARSING, include_suggestion=False)
        '收到分析数据但解析失败'
    """
    template = ERROR_MESSAGES.get(category, {
        "user": "发生错误",
        "suggestion": "请重试"
    })

    msg = template["user"]
    if include_suggestion:
        msg += f"。{template['suggestion']}"

    return msg


def get_detailed_error_message(
    category: ErrorCategory,
    context: str = "",
    include_suggestion: bool = True
) -> str:
    """
    Get error message with additional context.

    Args:
        category: Error category
        context: Additional context about the error
        include_suggestion: Whether to include suggestion text

    Returns:
        Detailed error message

    Example:
        >>> get_detailed_error_message(
        ...     ErrorCategory.AGENT_EXECUTION,
        ...     context="在趋势分析阶段"
        ... )
        '在趋势分析阶段:分析代理执行时遇到问题,无法完成分析。请重试一次,如果问题持续存在请联系技术支持'
    """
    msg = get_error_message(category, include_suggestion)

    if context:
        return f"{context}:{msg}"

    return msg

from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_QUERY = "INVALID_QUERY"
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    SANDBOX_VIOLATION = "SANDBOX_VIOLATION"
    CONCEPT_NOT_FOUND = "CONCEPT_NOT_FOUND"
    SECTION_NOT_FOUND = "SECTION_NOT_FOUND"
    INVALID_GRAPH_DEPTH = "INVALID_GRAPH_DEPTH"
    INVALID_LIMIT = "INVALID_LIMIT"
    INVALID_TOKEN_BUDGET = "INVALID_TOKEN_BUDGET"
    INDEX_NOT_READY = "INDEX_NOT_READY"
    MALFORMED_FRONTMATTER = "MALFORMED_FRONTMATTER"


class OKFError(Exception):
    code = ErrorCode.INVALID_QUERY

    def __init__(self, message: str, code: ErrorCode | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class OKFPathNotFound(OKFError):
    code = ErrorCode.PATH_NOT_FOUND


class OKFSandboxViolation(OKFError):
    code = ErrorCode.SANDBOX_VIOLATION


class OKFConceptNotFound(OKFError):
    code = ErrorCode.CONCEPT_NOT_FOUND


class OKFSectionNotFound(OKFError):
    code = ErrorCode.SECTION_NOT_FOUND


class OKFInvalidQuery(OKFError):
    code = ErrorCode.INVALID_QUERY

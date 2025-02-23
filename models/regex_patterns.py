from typing import Dict

# Pre-processing patterns
REGEX_MAP_PRE = {
    'upiid': r"((?:[-a-z\d_]+)(?:(?:[\.])(?:[-a-z\d_]+))*@(?:[a-z]+))",
    'pan': r"(\d*[xx\*]+\s*\-*\d+\-*[xx\*]*)",
    'date': r"(\d{1,4}[-/\.](?:(?:(?:[a-z\d]{3,9})|(?:\d{1,2})))[-/\.]\d{1,4})",
    'transactioncurrency': r"(\baed\b|\baud\b|\bbdt\b|\bbhd\b|\bbrl\b|\bcad\b|\beur\b|\bgbp\b|\bhkd\b|\bhuf\b|\bidr\b|\busd\b|\bmyr\b|\bsar\b|\bkwd\b|\bcny\b|\bthb\b|\bsgd\b|\bqar\b|\bomr\b|\bnpr\b|\bmvr\b|\blkr\b|\bjod\b|\bamd\b)",
    'amount': r"(?:Rs\s*\.\s*|Rs\s*:\s*|Rs|INR\.|INR|I@NR|₹|रु\.|रु|MRP)(?:[\s\.)()]*)((?:[+]?\s*(?:(?:[\d,，]+(?:\.\d+)?)|(?:\.\d+))))",
    'time': r"(?:\d{1,2}[\:\/]\d{1,2})(?:(?:[\:\/](?:(?:\d{1,2})?))?)(?:(?:\s)?)(?:(?:am|pm)?)",
}

# Post-processing patterns
REGEX_MAP_POST = {
    'generalpan': r"(?:lan|loan|policy|vi|card|customer)(?:\s*[account|agreement]*)?(?:\s*number)?(?:\s*is)?[<:\s]+([a-z-]*\d+[a-z-]*\d*)[>]*",
    'dpd': r"by\s+(\d+)\s*days|(\d+)\s*days\s*past",
    'generalamount': r"payment\s*of\s*(?:amount)?([-@:\\\.\?\*!~\(\),\[\]&%$#\w]+)",
    'generalcode': r"code\s*(?:is)*(?:[-@:\\\.\?\*!~\(\),\[\]&%$#\w]*)",
    'utrnumber': r"utr\s+(?:number)?\s*(?:[-@:\\\.\?\*!~\(\),\[\]&%$#\w]*)",
    'generalnumber': r"\b(\d+[\d,\.]*)\b"
}

# Transaction type patterns
TRANSACTION_PATTERNS = {
    'debit': r"debited|debit-ed|debits|debit",
    'credit': r"credited|credit-ed|credits|credit",
    'netbanking': r"mobile\s*banking|internet\s*banking|net\s*banking|net-banking|netbanking|e\s*-\s*banking|एन\s*\.*\s*ई\s*\.*\s*एफ\s*\.*\s*टी\s*\.*|एनईएफटी|mob\s*bk|neft|rtgs|imps|mob\s|\smbs|ib\.|\.ib|\.mb|mb\.",
    'autodebit': r"standing\s*instructions|standing\s*instruction|auto\s*debit|auto\s*\-\s*debited|auto\s*\-\s*debit|auto\s*-\s*payment|instr|e-mandate|autopay|mandate|enach|nach|cheque|ecs|si\s|si\.|si\(|si:",
    'creditcard': r"credit\s*card|cc\s|\bcc\.",
    'upi': r"\bupi\b|up\|",
}

# Common financial terms and entities
ENTITY_PATTERNS = {
    'account': r"account\.|account|acct\.|acct|\bacc\b|a/c\.|a/c|\bac\b",
    'reference': r"reference\.|reference:|reference|\bref\b|rrn\.*\s*:*",
    'available': r"available\.|available|avlbl\.|avlbl|avbl\.|avbl|avail\b|aval\.|\baval\b|avl\.|avl",
    'balance': r"balance\s*is:|balance\s*\.|balance\s*:|balance\s*-|balance\.\s*is|balance\s*is|balance\s*:\s*is|balance\s*-\s*is|balance|bal\s*is|bal\s*:|bal\s*-|bal\s*\.|bal\s*\.\s*is|bal\s*:\s*is|bal\s*-\s*is|bal|bl\.|bl:|bl\s",
}

# Combined map for all patterns
REGEX_MAP = {
    **REGEX_MAP_PRE,
    **REGEX_MAP_POST,
    **TRANSACTION_PATTERNS,
    **ENTITY_PATTERNS
}

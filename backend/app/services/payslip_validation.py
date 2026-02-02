class PayslipValidationError(Exception):
    pass


def validate_payslip(employee, gross: float, net: float):
    if employee.base_salary is None:
        raise PayslipValidationError("Base salary missing")

    if gross <= 0:
        raise PayslipValidationError("Gross pay must be > 0")

    if net < 0:
        raise PayslipValidationError("Net pay cannot be negative")

    if net > gross:
        raise PayslipValidationError("Net pay cannot exceed gross")

    # future rules go here

from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.conf import settings

class User(AbstractUser):
    class Roles(models.TextChoices):
        ROOT_DEV = 'ROOT_DEV', 'Root Developer'
        DEV      = 'DEV', 'Developer'
        ADMIN    = 'ADMIN', 'Admin'
        USER     = 'USER', 'User'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )
    mobile_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class ULB(models.Model):
    ULB_TYPES = [
        ('NAGAR_NIGAM', 'Nagar Nigam'),
        ('NAGAR_PARISHAD', 'Nagar Parishad'),
        ('NAGAR_PANCHAYAT', 'Nagar Panchayat'),
    ]

    ulb_name = models.CharField(max_length=255)
    ulb_type = models.CharField(max_length=20, choices=ULB_TYPES)
    email = models.EmailField()
    pan_no = models.CharField(max_length=20, blank=True, null=True)
    tin_no = models.CharField(max_length=20)
    gst_no = models.CharField(max_length=20)
    land_mark = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    date_of_creation = models.DateField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=10,unique=True,blank=True,null=True,help_text="Short code used in voucher numbers, e.g. DNP, SNN.")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ulb_name} ({self.get_ulb_type_display()})"


class UserPermission(models.Model):
    """
    Single table for both:
    - Level 1: which ULBs a user can access at all
      (store 'ULB_ACCESS' for that user + ulb)
    - Level 2: which menus/buttons are allowed for that user + ulb
      (store codes like 'MENU_VIEW_ULB', 'BTN_EDIT_ULB', etc.)
    """
    ULB_ACCESS_CODE = 'ULB_ACCESS'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permissions',
    )
    ulb = models.ForeignKey(
        ULB,
        on_delete=models.CASCADE,
        related_name='permissions',
    )
    code = models.CharField(
        max_length=100
    )  # e.g. 'ULB_ACCESS', 'MENU_VIEW_ULB', 'BTN_EDIT_ULB'

    class Meta:
        unique_together = ('user', 'ulb', 'code')

    def __str__(self):
        return f"{self.user} / {self.ulb} -> {self.code}"

    # ----- helpers for ULB access (step 1) -----

    @classmethod
    def ulbs_for_user(cls, user):
        """
        Return queryset of ULBs where this user has ULB_ACCESS.
        Used to ensure Developer/Admin/User only see permitted ULBs.
        """
        return ULB.objects.filter(
            permissions__user=user,
            permissions__code=cls.ULB_ACCESS_CODE,
        ).distinct()

    @classmethod
    def give_ulb_access(cls, user, ulb):
        """
        Ensure a ULB_ACCESS row exists for this user + ulb.
        """
        return cls.objects.get_or_create(
            user=user,
            ulb=ulb,
            code=cls.ULB_ACCESS_CODE,
        )[0]

    @classmethod
    def revoke_ulb_access(cls, user, ulb):
        """
        Remove ULB_ACCESS for this user + ulb.
        """
        cls.objects.filter(
            user=user,
            ulb=ulb,
            code=cls.ULB_ACCESS_CODE,
        ).delete()


#-------Ledger & grouping models -------
class HeadGroupChoices(models.IntegerChoices):
    INCOME = 1, "1 Income"
    EXPENSES = 2, "2 Expenses"
    LIABILITIES = 3, "3 Liabilities"
    ASSETS = 4, "4 Assets"


class LedgerGroup(models.Model):
    """
    Hierarchical group node.
    You can represent Group, Group-1, Group-2, Group-3, ... with unlimited depth.
    """
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("name", "parent")

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class SubGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class MainGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Ledger(models.Model):
    """
    Ledger with hierarchy:
    ledger -> (LedgerGroup chain: group, group1, group2, group3, ...) -> subgroup -> main_group -> head_group_code
    plus opening information (date, type, amount).
    """
    ulb = models.ForeignKey("accounts.ULB", on_delete=models.CASCADE, related_name="ledgers")

    name = models.CharField(max_length=255)

    # hierarchy: deepest group node in the chain (can be any level: group, group1, group2, group3, ...)
    group = models.ForeignKey(
        LedgerGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledgers",
    )

    subgroup = models.ForeignKey(
        SubGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledgers"
    )
    main_group = models.ForeignKey(
        MainGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="ledgers"
    )

    head_group_code = models.IntegerField(
        choices=HeadGroupChoices.choices,
        null=True,
        blank=True,
        help_text="1 Income, 2 Expenses, 3 Liabilities, 4 Assets",
    )

    # opening info for this ledger
    opening_date = models.DateField(null=True, blank=True)
    opening_type = models.CharField(
        max_length=2,
        choices=(("DR", "Debit"), ("CR", "Credit")),
        null=True,
        blank=True,
    )
    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_ledgers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ulb", "name")
        ordering = ["name"]

    def __str__(self):
        # use ULB.__str__ (which already returns "ulb_name (type)")
        return f"{self.name} ({self.ulb})"

class VoucherType(models.TextChoices):
    RECEIPT = 'RECV', 'Receipts'
    PAYMENT = 'PYMT', 'Payments'
    CONTRA = 'CNTR', 'Contra'
    JOURNAL = 'JRNL', 'Journal'

class Transaction(models.Model):
    ulb = models.ForeignKey(ULB, on_delete=models.CASCADE)
    voucher_type = models.CharField(max_length=10, choices=VoucherType.choices)
    voucher_date = models.DateField()
    voucher_no = models.CharField(max_length=50, unique=True)
    sequence_no = models.IntegerField()  # year-wise per ULB+type
    narration = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-voucher_date', 'voucher_no']

    def __str__(self):
        return f"{self.voucher_no} - {self.get_voucher_type_display()}"

class TransactionEntry(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    entry_type = models.CharField(max_length=2, choices=[('Dr', 'Dr'), ('Cr', 'Cr')])
    ledger = models.ForeignKey('Ledger', on_delete=models.CASCADE)
    dr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_brs_reconciled = models.BooleanField(default=False)
    brs_adjustment_id = models.PositiveIntegerField(null=True, blank=True)
    brs_cash_particulars = models.TextField(blank=True)

    class Meta:
        ordering = ['id']


class ReceiptUCDetails(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        limit_choices_to={'voucher_type': 'RECEIPT'},
    )
    uc_applicable = models.BooleanField(default=False)
    major_head = models.CharField(max_length=100, blank=True)
    treasury_code = models.CharField(max_length=50, blank=True)
    uc_bill_no = models.CharField(max_length=100, blank=True)
    uc_bill_date = models.DateField(null=True, blank=True)
    sub_major_head = models.CharField(max_length=100, blank=True)
    ddo_code = models.CharField(max_length=50, blank=True)
    letter_no = models.CharField(max_length=100, blank=True)
    letter_date = models.DateField(null=True, blank=True)
    minor_head = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=50, blank=True)
    tv_no = models.CharField(max_length=100, blank=True)
    tv_date = models.DateField(null=True, blank=True)
    sub_head = models.CharField(max_length=100, blank=True)
    bill_code = models.CharField(max_length=50, blank=True)
    grant_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class PaymentVendorDetails(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        limit_choices_to={'voucher_type': 'PAYMENT'},
    )
    vendor_name = models.CharField(max_length=255)
    vendor_amount = models.DecimalField(max_digits=15, decimal_places=2)
    cheque_no = models.CharField(max_length=50, blank=True)
    
    gst_applicable = models.BooleanField(default=False)
    gst_no = models.CharField(max_length=20, blank=True)
    gst_type = models.CharField(
        max_length=10,
        choices=[('inter', 'Inter State'), ('intra', 'Intra State')],
        blank=True,
    )
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    igst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    tds_applicable = models.BooleanField(default=False)
    tds_pan_no = models.CharField(max_length=20, blank=True)
    tds_section = models.CharField(max_length=10, blank=True)
    tds_nature = models.CharField(max_length=50, blank=True)
    tds_type = models.CharField(max_length=20, blank=True)
    tds_rate = models.CharField(max_length=10, blank=True)
    tds_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class BankReconciliationEntry(models.Model):
    """
    One manual BRS line for a bank ledger (450...) of a ULB.
    Captures: Dr/Cr type, Date, Bank narration, Dr amount / Cr amount (only one used per line)
    """
    
    ENTRY_TYPES = [
        ("Dr", "Debit"),
        ("Cr", "Credit"),
    ]

    ulb = models.ForeignKey(
        "accounts.ULB",
        on_delete=models.CASCADE,
        related_name="brs_entries",
    )
    ledger = models.ForeignKey(
        "accounts.Ledger",
        on_delete=models.CASCADE,
        related_name="brs_entries",
        help_text="Bank ledger (usually starting with 450...).",
    )

    entry_type = models.CharField(max_length=2, choices=ENTRY_TYPES)
    entry_date = models.DateField()
    bank_narration = models.TextField(blank=True)
    cheque_number = models.CharField(max_length=50, blank=True, null=True)

    dr_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Use when Type = Dr.",
    )
    cr_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Use when Type = Cr.",
    )
    is_reconciled = models.BooleanField(default=False)
    brs_adjustment_id = models.PositiveIntegerField(null=True, blank=True)
    brs_bank_particulars = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_brs_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-id"]

    def __str__(self):
        return f"BRS {self.ulb} / {self.ledger} {self.entry_date} {self.entry_type} {self.dr_amount or self.cr_amount}"

class FifteenthFinanceLedger(models.Model):
    ulb = models.ForeignKey(
        "accounts.ULB",
        on_delete=models.CASCADE,
        related_name="fifteenth_finance_mappings",
    )
    ledger = models.ForeignKey(
        "accounts.Ledger",
        on_delete=models.CASCADE,
        related_name="fifteenth_finance_mappings",
    )
    defined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # as on date and balance at that date
    as_on_date = models.DateField(null=True, blank=True)
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # allocation amounts
    amount_untied = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    amount_swm = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    amount_rhwr = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    amount_interest = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # last chosen ratio tag for this ledger (for UI default)
    last_ratio_type = models.CharField(max_length=20, null=True, blank=True)
    ratio_locked = models.BooleanField(
        default=False,
        help_text="If true, ratio select is locked in transaction view until user clicks Edit.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ulb", "ledger")

    def __str__(self):
        return f"{self.ulb} - {self.ledger}"

class FifteenthFinanceTxnRatio(models.Model):
    ulb = models.ForeignKey("accounts.ULB", on_delete=models.CASCADE)
    transaction = models.ForeignKey("accounts.Transaction", on_delete=models.CASCADE)
    ledger = models.ForeignKey("accounts.Ledger", on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("ulb", "transaction", "ledger")


class FifteenthFinanceTxnAllocation(models.Model):
    """
    One row per (tx, ledger, bucket) when you want to split amounts OR store full.
    """
    ulb = models.ForeignKey("accounts.ULB", on_delete=models.CASCADE)
    transaction = models.ForeignKey("accounts.Transaction", on_delete=models.CASCADE)
    ledger = models.ForeignKey("accounts.Ledger", on_delete=models.CASCADE)

    ratio_type = models.CharField(
        max_length=20,
        choices=[
            ("40", "40% - Untied"),
            ("30_swm", "30% - SWM"),
            ("30_rhwr", "30% - RHWR"),
            ("interest", "Interest"),
        ],
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)

class SixthFinanceLedger(models.Model):
    ulb = models.ForeignKey(
        "accounts.ULB",
        on_delete=models.CASCADE,
        related_name="sixth_finance_mappings",
    )
    ledger = models.ForeignKey(
        "accounts.Ledger",
        on_delete=models.CASCADE,
        related_name="sixth_finance_mappings",
    )
    defined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # as on date and balance at that date
    as_on_date = models.DateField(null=True, blank=True)
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # 6th FC allocation amounts (top + detailed buckets)
    # 1) Development fund - 30%
    amount_dev_total = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    #   a) Tied Fund 60% (of Development)
    amount_dev_tied_total = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    #       i) SWM 44% (of Tied)
    amount_dev_tied_swm = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    #       ii) Others 16% (of Tied)
    amount_dev_tied_others = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    #   b) Untied Fund 40% (of Development)
    amount_dev_untied = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    # 2) Maintenance Fund - 20%
    amount_maint = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    # 3) General Fund - 50%
    amount_general = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    # last chosen ratio tag for this ledger (for UI default – optional, like 15th FC)
    last_ratio_type = models.CharField(max_length=20, null=True, blank=True)
    ratio_locked = models.BooleanField(
        default=False,
        help_text=(
            "If true, ratio select is locked in transaction view until user clicks Edit."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ulb", "ledger")

    def __str__(self):
        return f"{self.ulb} - {self.ledger}"


class SixthFinanceTxnRatio(models.Model):
    ulb = models.ForeignKey("accounts.ULB", on_delete=models.CASCADE)
    transaction = models.ForeignKey("accounts.Transaction", on_delete=models.CASCADE)
    ledger = models.ForeignKey("accounts.Ledger", on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("ulb", "transaction", "ledger")


class SixthFinanceTxnAllocation(models.Model):
    """
    One row per (tx, ledger, bucket) when you want to split amounts OR store full.
    6th FC buckets follow:
    1) Development fund - 30%
        a) Tied Fund 60% (SWM 44%, Others 16%)
        b) Untied Fund 40%
    2) Maintenance Fund - 20%
    3) General Fund - 50%
    """

    ulb = models.ForeignKey("accounts.ULB", on_delete=models.CASCADE)
    transaction = models.ForeignKey("accounts.Transaction", on_delete=models.CASCADE)
    ledger = models.ForeignKey("accounts.Ledger", on_delete=models.CASCADE)

    ratio_type = models.CharField(
        max_length=32,
        choices=[
            # top‑level
            ("DEV_TOTAL", "Development Fund (30%)"),
            ("MAINT", "Maintenance Fund (20%)"),
            ("GENERAL", "General Fund (50%)"),
            # detail level
            ("DEV_TIED_TOTAL", "Development Tied Fund (60% of Dev)"),
            ("DEV_TIED_SWM", "Development Tied - SWM (44% of Tied)"),
            ("DEV_TIED_OTHERS", "Development Tied - Others (16% of Tied)"),
            ("DEV_UNTIED", "Development Untied Fund (40% of Dev)"),
        ],
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return f"{self.ulb} / {self.ledger} / {self.transaction_id} / {self.ratio_type}"
    
class ReceiptUCUtilization(models.Model):
    """
    One per UC (receipt), tracks how much from the grant is utilized via payments.
    """
    receipt_uc = models.OneToOneField(
        ReceiptUCDetails,
        on_delete=models.CASCADE,
        related_name='utilization',
    )
    utilized_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"UC Utilization for {self.receipt_uc.letter_no or self.receipt_uc.id}"


from django.utils import timezone

class ReceiptUCUtilization(models.Model):
    """
    One row per UC save (per click on Save in uc_prepared).
    Same UC (ReceiptUCDetails) can have many utilizations (history).
    """
    receipt_uc = models.ForeignKey(
        ReceiptUCDetails,
        on_delete=models.CASCADE,
        related_name='utilizations',
    )
    utilized_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # UC prepared datetime (when you click Save)
    uc_date = models.DateTimeField(default=timezone.now)

    uc_identifier = models.CharField(max_length=50, blank=True)  # keep if you use it

    def __str__(self):
        base = self.receipt_uc.letter_no or self.receipt_uc.id
        return f"UC Utilization for {base} on {self.uc_date}"


class ReceiptUCUtilizationLine(models.Model):
    utilization = models.ForeignKey(
        ReceiptUCUtilization,
        on_delete=models.CASCADE,
        related_name='lines',
        null=True,     # allow null to satisfy existing rows
        blank=True,
    )
    # remove the old receipt_uc FK once you’ve migrated data, but for now keep it if it exists
    # receipt_uc = models.ForeignKey(...)

    payment_txn = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        limit_choices_to={'voucher_type': VoucherType.PAYMENT},
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_on = models.DateField()
    uc_identifier = models.CharField(max_length=50)



class PaymentUCUsage(models.Model):
    """
    Tracks how much of each PAYMENT transaction is tied to UCs.
    """
    payment_txn = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='uc_usage',
        limit_choices_to={'voucher_type': VoucherType.PAYMENT},
    )
    used_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_locked = models.BooleanField(default=False)  # fully used for UC

    def remaining_amount(self):
        total = self.payment_txn.paymentvendordetails.vendor_amount
        return max(Decimal('0.00'), total - (self.used_amount or Decimal('0.00')))

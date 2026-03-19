from zipfile import Path
from django.urls import path
from . import views
from .views import create_user_view, show_bank_entry_view, transaction_duplicate, uc_prepared, uc_undo_last, ulb_wise_report_view

urlpatterns = [
    # main router
    path('', views.dashboard, name='dashboard'),
    path('root-dashboard/', views.root_developer_dashboard, name='root_dashboard'),
    path('developer-dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('create-ulb/', views.create_ulb, name='create_ulb'),
    path('open-ulb/', views.open_ulb, name='open_ulb'),
    path('view-ulb/', views.view_ulb, name='view_ulb'),
    path('view-ulb/<int:ulb_id>/', views.view_ulb, name='view_ulb'),
    path('ulb-wise-report/',  ulb_wise_report_view, name='ulb_wise_report'),
    path('user-wise-report/',  views.user_wise_report_view, name='user_wise_report'),
    path('change-password/', views.change_password, name='change_password'),
    path('create-user/', create_user_view, name='create_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/<int:user_id>/action/', views.manage_user_action, name='manage_user_action'),
    path('manage-access/', views.manage_access, name='manage_access'),
    path('accounts/dashboard/', views.base_accounts_dashboard_view, name='base_accounts_dashboard'),
    path('accounts/master/', views.accounts_master_tabs, name='accounts_master_tabs'),
# Master tabs
    path('accounts/master/create/', views.accounts_master_home, name='accounts_master_home'),
    path('accounts/master/view-edit/', views.accounts_master_view_edit, name='accounts_master_view_edit'),
    path('accounts/master/export/', views.accounts_master_export, name='accounts_master_export'),
    path('accounts/master/import/', views.accounts_master_import, name='accounts_master_import'),
# Accounts Transaction Entry, Trial Balance, Income & Expenditure, Balance Sheet, Day Book, Ledger, GST Report, TDS Report, BRS)
    path('accounts/transaction_entry/', views.transaction_entry, name='accounts_transaction_entry'),
    path('accounts/transaction_entry/next-voucher/', views.get_next_voucher_no, name='next_voucher_no'),
    path('accounts/trial-balance/', views.trial_balance, name='accounts_trial_balance'),
    path('accounts/trial-balance/export-excel/', views.trial_balance_export_excel, name='trial_balance_export_excel'),
    path('accounts/income-expenditure/', views.income_expenditure, name='accounts_income_expenditure'),
    path('accounts/income-expenditure/export-excel/', views.income_expenditure_export_excel, name='income_expenditure_export_excel'),
    path('accounts/balance-sheet/', views.balance_sheet, name='accounts_balance_sheet'),
    path('accounts/balance-sheet/export-excel/', views.balance_sheet_export_excel, name='balance_sheet_export_excel'),
    path('accounts/day-book/', views.day_book, name='accounts_day_book'),
    path('accounts/transaction-edit/<int:txn_id>/', views.transaction_edit, name='accounts_transaction_edit'),
    path('accounts/transaction-duplicate/<int:txn_id>/', views.transaction_duplicate, name='accounts_transaction_duplicate'),
    path('accounts/cash-book/', views.cash_book, name='accounts_cash_book'),
    path('accounts/ledger/', views.ledger, name='accounts_ledger'),
    path('accounts/gst-report/', views.gst_report, name='accounts_gst_report'),
    path('accounts/tds-report/', views.tds_report, name='accounts_tds_report'),
    path('accounts/brs/', views.accounts_brs, name='accounts_brs'),
    path('accounts/brs/bank-entry/', views.bank_entry, name='accounts_bank_entry'),
    path("accounts/brs/show-bank-entry/", view=show_bank_entry_view, name="accounts_brs_show_bank_entry"),
    path('accounts/brs/brs-adjustment/', views.brs_adjustment, name='accounts_brs_adjustment'),
    path('accounts/brs/show-brs-adjustment/', views.show_brs_adjustment, name='accounts_show_brs_adjustment'),
    path('accounts/brs/adjustment/undo/<int:adjustment_id>/', views.brs_adjustment_undo, name='accounts_brs_adjustment_undo'),
    path('accounts/brs/statement/', views.brs_statement, name='accounts_brs_statement'),
    path("accounts/base_report/", views.base_reports, name="accounts_base_report"),
#Reports 15th Finance Commission, 
    path("reports/15th-finance/", views.fifteenth_finance_commission, name="fifteenth_finance_commission"),
    path('reports/15th-finance/define/', views.fifteenth_finance_commission_define, name='fifteenth_finance_commission_define'),
    path("reports/15th-finance/transactions/", views.fifteenth_finance_transaction_define, name="fifteenth_finance_transaction_define",),
    path('reports/15th-finance/report/', views.fifteenth_fc_report, name='fifteenth_finance_commission_report'),
#Reports 6th Finance Commission
    path("reports/6th-finance/", views.sixth_finance_commission, name="sixth_finance_commission"),
    path("reports/6th-finance/define/", views.sixth_finance_commission_define, name="sixth_finance_commission_define"),
    path("reports/6th-finance/transactions/", views.sixth_finance_transaction_define, name="sixth_finance_transaction_define"),
    path("reports/6th-finance/report/",views.sixth_fc_report, name="sixth_fc_report"),
# Utilization Certificate
    path("reports/utilization-certificate/prepared/", views.uc_prepared, name="uc_prepared"),
    path("reports/uc-report/", views.uc_report, name="uc_report"),
    path("reports/utilization-certificate/prepared/",views.uc_prepared,name="utilization_certificate"),

# Undo (Open) + export
    path("reports/uc-report/<int:util_id>/undo/", uc_undo_last, name="uc_undo_last"),
    path("uc/report/<int:util_id>/export-excel/",views.uc_report_export_excel,name="uc_report_export_excel"),
    path("reports/utilization-certificate/btc42a/", views.uc_btc42a_form, name="uc_btc42a_form"),
    


]


    

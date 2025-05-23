from odoo import SUPERUSER_ID
from odoo.exceptions import UserError

def create_sa_lp_user(env, lp_admin_group):

    """Tạo user quản trị viên Long Phượng"""

    if not lp_admin_group:
        raise UserError("Nhóm lp_admin chưa được tạo!")

    admin_group = env.ref("base.group_system")
    erp_manager_group = env.ref("base.group_erp_manager")

    admin_user = env["res.users"].browse(SUPERUSER_ID)
    admin_groups = admin_user.groups_id.filtered(lambda g: g.id != admin_group.id)

    all_groups = admin_groups | lp_admin_group

    all_companies = env["res.company"].search([])
    allowed_companies = all_companies.ids

    new_user_vals = {
        "name": "Quản trị viên Long Phượng",
        "login": "lp_admin",
        "password": "1",
        "email": "lp_admin@gmail.com",
        "company_ids": [(6, 0, allowed_companies)],
        "groups_id": [(6, 0, all_groups.ids)],
        "lang": "vi_VN",
    }

    cloned_user = env["res.users"].sudo().create(new_user_vals)

    cloned_user.sudo().write({
        "groups_id": [(3, admin_group.id), (3, erp_manager_group.id)]
    })

    return cloned_user

def create_lp_thu_kho_users(env, lp_thu_kho_hcm_group):
    
    company_1 = env["res.company"].browse(1)

    account_invoice_group = env.ref("account.group_account_invoice")
    stock_user_group = env.ref("stock.group_stock_user")

    users_data = [
        {
            "name": "[HCM] Trâm Xe Long Phượng",
            "login": "tram",
            "password": "1",
            "email": "tram@gmail.com",
            "company_id": company_1.id,
            "company_ids": [(6, 0, company_1.ids)],
            "groups_id": [(6, 0, [lp_thu_kho_hcm_group.id, account_invoice_group.id, stock_user_group.id])],
            "lang": "vi_VN",
        }
    ]

    created_users = []
    for user_vals in users_data:
        created_users.append(env["res.users"].sudo().create(user_vals))
    
    return created_users

def create_sa_users(env, lp_warehouse_assistant_hcm_group):
    company_1 = env["res.company"].browse(1)
    
    users_data = [
        {
            "name": "SA1 Xe Long Phượng",
            "login": "sa1",
            "password": "1",
            "email": "sa1@gmail.com",
            "company_id": company_1.id,
            "company_ids": [(6, 0, company_1.ids)],
            "groups_id": [(6, 0, [lp_warehouse_assistant_hcm_group.id])],
            "lang": "vi_VN",
        },
        {
            "name": "SA2 Xe Long Phượng",
            "login": "sa2",
            "password": "1",
            "email": "sa2@gmail.com",
            "company_id": company_1.id,
            "company_ids": [(6, 0, company_1.ids)],
            "groups_id": [(6, 0, [lp_warehouse_assistant_hcm_group.id])],
            "lang": "vi_VN",
        }
    ]
    
    created_users = []
    for user_vals in users_data:
        created_users.append(env["res.users"].sudo().create(user_vals))
    
    return created_users

def create_lp_user(env, lp_user_group):
    company_1 = env["res.company"].browse(1)
    
    if not lp_user_group:
        return None

    user_data = {
        "name": "Nhân viên Xe Long Phượng",
        "login": "user",
        "password": "1",
        "email": "user@gmail.com",
        "company_id": company_1.id,
        "company_ids": [(6, 0, company_1.ids)],
        "groups_id": [(6, 0, [lp_user_group.id])],
        "lang": "vi_VN",
    }

    return env["res.users"].sudo().create(user_data)

def create_lp_admin_cam_user(env, lp_admin_cam_group):
    company_1 = env["res.company"].browse(1)
    
    if not lp_admin_cam_group:
        return None

    user_data = {
        "name": "Oanh Xe Long Phượng",
        "login": "oanh",
        "password": "1",
        "email": "oanh@gmail.com",
        "company_id": company_1.id,
        "company_ids": [(6, 0, company_1.ids)],
        "groups_id": [(6, 0, [lp_admin_cam_group.id])],
        "lang": "vi_VN",
    }

    return env["res.users"].sudo().create(user_data)

def create_lp_thu_kho_cam_users(env, lp_thu_kho_cam_group):
    company_1 = env["res.company"].browse(1)
    
    if not lp_thu_kho_cam_group:
        return None

    user_data_1 = {
        "name": "Lượng Xe Long Phượng",
        "login": "luong",
        "password": "1",
        "email": "luong@gmail.com",
        "company_id": company_1.id,
        "company_ids": [(6, 0, company_1.ids)],
        "groups_id": [(6, 0, [lp_thu_kho_cam_group.id])],
        "lang": "vi_VN",
    }

    user_data_2 = {
        "name": "Tình Xe Long Phượng",
        "login": "tinh",
        "password": "1",
        "email": "nguyenvanb@gmail.com",
        "company_id": company_1.id,
        "company_ids": [(6, 0, company_1.ids)],
        "groups_id": [(6, 0, [lp_thu_kho_cam_group.id])],
        "lang": "vi_VN",
    }

    user_1 = env["res.users"].sudo().create(user_data_1)
    user_2 = env["res.users"].sudo().create(user_data_2)

    return user_1, user_2

def create_lp_admin_cam_tram_user(env, lp_admin_cam_tram_group):
    company_1 = env["res.company"].browse(1)
    
    if not lp_admin_cam_tram_group:
        return None

    user_data = {
        "name": "[CAM] Trâm Xe Long Phượng",
        "login": "tram_cam",
        "password": "1",
        "email": "tram_cam@gmail.com",
        "company_id": company_1.id,
        "company_ids": [(6, 0, company_1.ids)],
        "groups_id": [(6, 0, [lp_admin_cam_tram_group.id])],
        "lang": "vi_VN",
    }

    user = env["res.users"].sudo().create(user_data)

    return user

def pre_init_create_user_groups(env):
    # Lấy hoặc tạo nhóm nếu chưa có
    lp_admin_group = env.ref("group_permission_lp.group_lp_admin", raise_if_not_found=False)
    lp_thu_kho_hcm_group = env.ref("group_permission_lp.group_lp_admin_hcm", raise_if_not_found=False)
    lp_user_group = env.ref("group_permission_lp.group_lp_user_hcm", raise_if_not_found=False)
    lp_warehouse_assistant_hcm_group = env.ref("group_permission_lp.group_lp_assistant_hcm", raise_if_not_found=False)
    lp_admin_cam_group = env.ref("group_permission_lp.group_lp_admin_cam", raise_if_not_found=False)
    lp_thu_kho_cam_group = env.ref("group_permission_lp.group_lp_cam", raise_if_not_found=False)
    lp_admin_cam_tram_group = env.ref("group_permission_lp.group_lp_admin_cam_tram", raise_if_not_found=False)

    # Tạo user và gán vào nhóm
    create_sa_lp_user(env, lp_admin_group)
    create_lp_thu_kho_users(env, lp_thu_kho_hcm_group)
    create_lp_user(env, lp_user_group)
    create_sa_users(env, lp_warehouse_assistant_hcm_group)
    create_lp_admin_cam_user(env, lp_admin_cam_group)
    create_lp_thu_kho_cam_users(env, lp_thu_kho_cam_group)
    create_lp_admin_cam_tram_user(env, lp_admin_cam_tram_group)
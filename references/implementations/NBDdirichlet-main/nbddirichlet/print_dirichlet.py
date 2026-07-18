# print_dirichlet

def print_dirichlet(x):
    print("Dirichlet Model Parameters:")
    print(f"Category Penetration: {x.cat_pen}")
    print(f"Category Buy Rate: {x.cat_buyrate}")
    print(f"M: {x.M:.2f}")
    print(f"K: {x.K:.2f}")
    print(f"S: {x.S:.2f}")
    print("\nBrand Information:")
    for i, brand in enumerate(x.brand_name):
        print(f"{brand}:")
        print(f"  Share: {x.brand_share[i]:.4f}")
        print(f"  Observed Penetration: {x.brand_pen_obs[i]:.4f}")
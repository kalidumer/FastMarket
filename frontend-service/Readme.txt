frontend-service/
├── src/
│   ├── assets/              # Logos, default placeholder icons, payment badges
│   ├── components/          # Reusable UI elements (Button, Input, Navbar, Footer)
│   ├── config/              # Central configuration constants
│   │   └── constants.ts     # Gateway Base URL and payment endpoint constants
│   ├── features/            # Isolated core business domains
│   │   ├── auth/
│   │   │   ├── components/  # LoginForm, SignupForm
│   │   │   ├── authSlice.ts # Authentication global state
│   │   │   └── authService.ts
│   │   ├── catalog/         # Product discovery & details listing
│   │   │   ├── components/  # ProductCard, ProductGrid, FilterSidebar
│   │   │   ├── catalogSlice.ts
│   │   │   └── catalogService.ts
│   │   ├── cart/            # Client side persistence & cart calculations
│   │   │   ├── components/  # CartDrawer, CartItemRow
│   │   │   └── cartSlice.ts # Handles local state (Redux Toolkit)
│   │   └── checkout/        # Payment gateway interactions & handshakes
│   │       ├── components/  # OrderSummary, CheckoutForm
│   │       ├── checkoutSlice.ts
│   │       └── checkoutService.ts # Chapa initiation API calls
│   ├── layouts/             # Root structural layouts (e.g., MarketLayout, AuthLayout)
│   ├── pages/               # Clean route targets aggregating specific features
│   │   ├── home/
│   │   │   └── index.tsx    # Customer landing experience
│   │   ├── product-detail/
│   │   │   └── index.tsx    # Single product views
│   │   ├── login/
│   │   │   └── index.tsx
│   │   ├── cart-page/
│   │   │   └── index.tsx
│   │   └── payment-status/  # Landing pad for Chapa callback redirect status hooks
│   │       ├── Success.tsx
│   │       └── Verify.tsx
│   ├── store/               # Redux Central Configuration Hub
│   │   └── store.ts         # Integrates: auth, catalog, cart, and checkout reducers
│   ├── utils/               # App-wide utility blocks
│   │   └── api.ts           # Axios base instance featuring interceptors
│   ├── App.tsx              # Router composition core mapping
│   ├── main.tsx             # Mounting layout wrapped with Redux Provider
│   └── index.css
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
└── package.json
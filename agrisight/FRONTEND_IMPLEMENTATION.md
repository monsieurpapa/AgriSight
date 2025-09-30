# AgriSight Frontend Implementation Guide

## Overview
## Public Landing & Demo (MVP)

- Route `/landing`:
  - Marketing landing page with hero, feature grid, use-cases, pricing CTA, FAQ, and footer links.
  - Primary CTA: "Try it now" → `/register`. Secondary CTA: "View demo" → `/demo`.
  - Screenshot strip added, using static assets under `frontend/public/demo/`.

- Route `/demo`:
  - Read-only public demo.
  - Loads NDVI sample data from `public/demo/ndvi.json` and renders a line chart with Recharts.
  - Displays a map preview (`public/demo/map-preview.svg`) to illustrate overlays and AOIs.
  - No backend/API calls; suitable for unauthenticated exploration.

- Auth gating:
  - Unauthenticated users are redirected to `/landing` when accessing protected routes.
  - Authenticated users visiting public routes may be redirected to `/` (Dashboard).

## Routes Overview

- Public: `/landing`, `/demo`, `/login`, `/register`, `/forgot-password`, `/privacy`, `/terms`, `/support`.
- Protected (behind layout): `/` (Dashboard), `/map`, `/regions`, `/satellite`, `/vegetation`, `/analytics`, `/stress-events`, `/alerts`, `/reports`, `/exports`, `/organizations`, `/admin/settings`, `/admin/performance`, `/profile`, `/settings`.

## Static Assets

Located in `frontend/public/demo/`:

- `ndvi.json`: Sample NDVI time series.
- `map-preview.svg`: Map UI illustration (legend, AOIs, layers strip).
- `screenshot-1.svg`: Dashboard mock screenshot.
- `screenshot-2.svg`: Map mock screenshot.

## Components Updated

- `src/pages/Landing.jsx`:
  - Adds screenshot strip and CTA wiring to `/register` and `/demo`.

- `src/pages/PublicDemo.jsx`:
  - Fetches `ndvi.json` and renders a `LineChart` (Recharts).
  - Shows `map-preview.svg` image.

- `src/App.jsx`:
  - Adds routes for `/landing` and `/demo`.
  - Updates unauthenticated redirect to `/landing`.

## MVP Notes

- Social auth buttons in `Login.jsx` are controlled by backend `authConfig.social_providers`. They remain hidden unless enabled.
- Public demo is intentionally static and offline-friendly; integrate real data later without changing the public contract.


This document provides a comprehensive guide to the AgriSight frontend implementation, a professional React-based agricultural monitoring platform designed for humanitarian organizations operating in DRC conflict zones.

## Architecture Overview

### Technology Stack

- **React 18** - Modern functional components with hooks
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality, accessible component library
- **React Router** - Client-side routing
- **TanStack Query** - Server state management
- **Recharts** - Data visualization library
- **Lucide React** - Icon library
- **Axios** - HTTP client for API communication
- **date-fns** - Date manipulation library

### Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx          # Main navigation header
│   │   │   ├── Sidebar.jsx         # Navigation sidebar
│   │   │   └── Layout.jsx          # Main layout wrapper
│   │   └── ui/                     # shadcn/ui components
│   ├── contexts/
│   │   └── AuthContext.jsx         # Authentication state management
│   ├── lib/
│   │   ├── api.js                  # API service layer
│   │   └── utils.js                # Utility functions
│   ├── pages/
│   │   ├── Dashboard.jsx           # Main dashboard
│   │   └── Login.jsx               # Authentication page
│   ├── App.jsx                     # Main application component
│   ├── App.css                     # Global styles
│   └── main.jsx                    # Application entry point
├── .env                            # Environment configuration
├── Dockerfile                      # Production container
├── nginx.conf                      # Production web server config
└── package.json                    # Dependencies and scripts
```

## Key Features Implemented

### 1. Authentication System

#### Login Page (`src/pages/Login.jsx`)
- **Professional Design**: Clean, centered layout with AgriSight branding
- **Form Validation**: Email and password validation with error handling
- **Demo Credentials**: Built-in demo accounts for testing
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Security Features**: Password visibility toggle, remember me option

#### Authentication Context (`src/contexts/AuthContext.jsx`)
- **State Management**: Comprehensive auth state with useReducer
- **Token Handling**: Automatic token storage and refresh
- **Role-Based Access**: Permission and role checking utilities
- **Error Handling**: Comprehensive error states and user feedback

### 2. Layout System

#### Header Component (`src/components/layout/Header.jsx`)
- **Responsive Navigation**: Mobile hamburger menu, desktop full nav
- **User Menu**: Profile dropdown with logout functionality
- **Notifications**: Alert system with badge indicators
- **Organization Info**: Context-aware organization display

#### Sidebar Component (`src/components/layout/Sidebar.jsx`)
- **Hierarchical Navigation**: Organized by functional areas
- **Role-Based Menus**: Dynamic menu items based on user permissions
- **Active State Indicators**: Visual feedback for current page
- **Mobile Responsive**: Collapsible sidebar for mobile devices

#### Layout Wrapper (`src/components/layout/Layout.jsx`)
- **Consistent Structure**: Header, sidebar, and main content areas
- **Mobile Menu Management**: State management for mobile navigation
- **Responsive Behavior**: Adaptive layout for different screen sizes

### 3. Dashboard Interface

#### Main Dashboard (`src/pages/Dashboard.jsx`)
- **Statistics Cards**: Key metrics with visual indicators
- **Data Visualization**: Interactive charts using Recharts
- **Recent Activity**: Timeline of system events
- **Region Performance**: Agricultural health monitoring
- **Quick Actions**: Common task shortcuts

#### Chart Components
- **Line Charts**: Vegetation index trends over time
- **Pie Charts**: Regional health status distribution
- **Bar Charts**: Comparative analysis displays
- **Responsive Design**: Charts adapt to container sizes

### 4. API Integration Layer

#### API Service (`src/lib/api.js`)
- **Axios Configuration**: Centralized HTTP client setup
- **Authentication Interceptors**: Automatic token injection
- **Error Handling**: Comprehensive error response processing
- **Service Classes**: Organized API endpoints by functionality

#### Supported API Endpoints
- **Authentication**: Login, logout, user management
- **Organizations**: Multi-tenant organization management
- **Regions**: Geographic area management
- **Satellite Data**: Imagery and processing status
- **Vegetation Indices**: NDVI, EVI, NDWI, SAVI data
- **Stress Events**: Agricultural anomaly detection
- **Reports**: Document generation and export
- **Alerts**: Notification management

### 5. Utility Functions

#### Date and Time (`src/lib/utils.js`)
- **Date Formatting**: Consistent date display across application
- **Relative Time**: Human-readable time differences
- **Time Zone Handling**: Proper UTC/local time conversion

#### Vegetation Index Utilities
- **Color Coding**: Visual indicators for health levels
- **Label Generation**: Human-readable status descriptions
- **Value Formatting**: Consistent decimal precision

#### Data Formatting
- **Number Formatting**: Locale-aware number display
- **Area Calculations**: Hectares and square kilometers
- **Coordinate Display**: Latitude/longitude formatting

## Styling and Design

### Design System

#### Color Palette
- **Primary Green**: Agricultural theme with green accents
- **Status Colors**: Red (critical), yellow (warning), green (healthy)
- **Neutral Grays**: Professional background and text colors
- **Dark Mode**: Complete dark theme support

#### Typography
- **Font Stack**: System fonts for optimal performance
- **Hierarchy**: Clear heading and body text distinction
- **Responsive Sizing**: Scalable text for different devices

#### Component Styling
- **Consistent Spacing**: Tailwind CSS spacing scale
- **Border Radius**: Consistent rounded corners
- **Shadows**: Subtle depth indicators
- **Hover States**: Interactive feedback

### Custom CSS Classes

#### Agricultural Theme Classes
```css
.agri-green { @apply text-green-600 dark:text-green-400; }
.agri-yellow { @apply text-yellow-600 dark:text-yellow-400; }
.agri-red { @apply text-red-600 dark:text-red-400; }
```

#### Vegetation Index Indicators
```css
.ndvi-high { @apply bg-green-500 text-white; }
.ndvi-medium { @apply bg-yellow-500 text-white; }
.ndvi-low { @apply bg-red-500 text-white; }
```

#### Status Indicators
```css
.status-online { @apply bg-green-100 text-green-800; }
.status-processing { @apply bg-yellow-100 text-yellow-800; }
.status-offline { @apply bg-red-100 text-red-800; }
```

## Responsive Design

### Breakpoint Strategy
- **Mobile First**: Base styles for mobile devices
- **Tablet**: md: breakpoint for tablet layouts
- **Desktop**: lg: and xl: for larger screens
- **Touch Friendly**: Larger touch targets for mobile

### Component Responsiveness
- **Navigation**: Hamburger menu on mobile, full sidebar on desktop
- **Charts**: Responsive containers with appropriate sizing
- **Tables**: Horizontal scrolling on mobile devices
- **Forms**: Stacked layouts on small screens

## Performance Optimization

### Code Splitting
- **Route-Based**: Lazy loading for page components
- **Component-Level**: Dynamic imports for heavy components
- **Library Splitting**: Separate chunks for large dependencies

### Bundle Optimization
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Image and font compression
- **Caching Strategy**: Long-term caching for static assets

### Development Performance
- **Hot Module Replacement**: Fast development iteration
- **Source Maps**: Debugging support in development
- **Build Optimization**: Production-ready builds

## Production Deployment

### Docker Configuration

#### Multi-Stage Build (`Dockerfile`)
```dockerfile
# Build stage
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration (`nginx.conf`)
- **Static File Serving**: Optimized for React SPA
- **Client-Side Routing**: Proper fallback to index.html
- **Compression**: Gzip compression for assets
- **Security Headers**: XSS protection and content security policy
- **API Proxy**: Backend API proxying for production

### Environment Configuration

#### Development (`.env`)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=AgriSight
VITE_DEBUG=true
```

#### Production
```bash
VITE_API_URL=https://api.agrisight.org/api
VITE_APP_NAME=AgriSight
VITE_DEBUG=false
```

## Integration with Backend

### API Communication
- **Base URL Configuration**: Environment-specific API endpoints
- **Authentication Headers**: Automatic token injection
- **Error Handling**: Comprehensive error response processing
- **Retry Logic**: Automatic retry for failed requests

### Data Flow
1. **User Authentication**: Login flow with token storage
2. **Data Fetching**: TanStack Query for server state management
3. **Real-time Updates**: WebSocket support for live data
4. **Offline Support**: Service worker for offline functionality

### Backend Dependencies
- **Django REST API**: RESTful API endpoints
- **Token Authentication**: JWT or Django token auth
- **CORS Configuration**: Cross-origin request support
- **WebSocket Support**: Real-time data updates

## Testing Strategy

### Component Testing
- **React Testing Library**: Component behavior testing
- **Jest**: Unit test framework
- **Mock Service Worker**: API mocking for tests

### Integration Testing
- **Cypress**: End-to-end testing framework
- **User Flow Testing**: Complete user journey validation
- **Cross-Browser Testing**: Compatibility across browsers

### Performance Testing
- **Lighthouse**: Performance auditing
- **Bundle Analysis**: Bundle size monitoring
- **Load Testing**: Performance under load

## Accessibility

### WCAG 2.1 AA Compliance
- **Semantic HTML**: Proper HTML structure
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: Sufficient contrast ratios

### Inclusive Design
- **Colorblind Support**: Colorblind-friendly palettes
- **Text Scaling**: Scalable text and UI elements
- **Focus Indicators**: Clear focus states
- **Alternative Text**: Image descriptions

## Security Considerations

### Frontend Security
- **XSS Prevention**: Content Security Policy implementation
- **CSRF Protection**: Token-based request validation
- **Secure Storage**: Secure token storage practices
- **Input Validation**: Client-side validation with server verification

### Data Protection
- **Sensitive Data**: Minimal client-side storage
- **Encryption**: HTTPS enforcement
- **Session Management**: Secure session handling
- **Audit Logging**: User action tracking

## Future Enhancements

### Phase 1 (Short-term)
- **Map Integration**: Leaflet maps with satellite overlays
- **Real-time Data**: WebSocket integration for live updates
- **Mobile App**: React Native mobile application
- **Offline Support**: Progressive Web App features

### Phase 2 (Medium-term)
- **Advanced Analytics**: Machine learning insights
- **Collaboration Tools**: Multi-user collaboration features
- **Custom Dashboards**: User-configurable dashboards
- **API Documentation**: Interactive API documentation

### Phase 3 (Long-term)
- **AI Integration**: Predictive analytics and recommendations
- **Third-party Integrations**: External system connections
- **Global Expansion**: Multi-language support
- **Advanced Visualization**: 3D mapping and visualization

## Maintenance and Support

### Code Quality
- **ESLint Configuration**: Code quality enforcement
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for quality checks
- **TypeScript Migration**: Gradual TypeScript adoption

### Documentation
- **Component Documentation**: Storybook integration
- **API Documentation**: OpenAPI/Swagger integration
- **User Guides**: End-user documentation
- **Developer Guides**: Technical documentation

### Monitoring
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Monitoring**: Real User Monitoring (RUM)
- **Analytics**: User behavior analytics
- **Health Checks**: Application health monitoring

## Conclusion

The AgriSight frontend provides a comprehensive, production-ready interface for agricultural monitoring in DRC conflict zones. The implementation demonstrates enterprise-grade quality with:

- **Professional Design**: Clean, intuitive interface suitable for humanitarian organizations
- **Scalable Architecture**: Modular, maintainable codebase
- **Performance Optimization**: Fast loading and responsive user experience
- **Accessibility Compliance**: Inclusive design for all users
- **Security Best Practices**: Secure handling of sensitive data
- **Integration Ready**: Seamless backend integration capabilities

The platform successfully addresses the unique needs of agricultural monitoring in challenging environments while providing a modern, reliable tool for humanitarian organizations and agricultural stakeholders.


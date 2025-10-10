import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  AlertTitle,
  IconButton,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  Warning as WarningIcon,
  ShoppingCart as ShoppingCartIcon,
  TrendingDown as TrendingDownIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';

interface InventoryItem {
  id: number;
  name: string;
  category: string;
  quantity: number;
  minQuantity: number;
  unit: string;
  price: number;
  expirationDate?: string;
  status: 'healthy' | 'low' | 'critical' | 'expiring';
}

interface StockAlert {
  id: number;
  productName: string;
  currentQty: number;
  minQty: number;
  alertType: string;
  severity: 'high' | 'medium' | 'low';
}

interface InventoryDashboardProps {
  organizationId: number;
}

const InventoryDashboard: React.FC<InventoryDashboardProps> = ({ organizationId }) => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [alerts, setAlerts] = useState<StockAlert[]>([]);
  const [valuation, setValuation] = useState({ totalCost: 0, totalValue: 0, potentialProfit: 0 });
  const [loading, setLoading] = useState(true);
  const [purchaseOrderOpen, setPurchaseOrderOpen] = useState(false);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  useEffect(() => {
    loadInventoryData();
  }, [organizationId]);

  const loadInventoryData = async () => {
    setLoading(true);
    try {
      // In real implementation, these would be API calls
      // For now, using mock data
      
      // Mock inventory
      const mockInventory: InventoryItem[] = [
        {
          id: 1,
          name: 'כפפות לטקס',
          category: 'ציוד מגן',
          quantity: 5,
          minQuantity: 20,
          unit: 'קופסה',
          price: 45,
          status: 'critical',
        },
        {
          id: 2,
          name: 'מסכות כירורגיות',
          category: 'ציוד מגן',
          quantity: 15,
          minQuantity: 30,
          unit: 'קופסה',
          price: 35,
          status: 'low',
        },
        {
          id: 3,
          name: 'אנסתזיה מקומית',
          category: 'תרופות',
          quantity: 25,
          minQuantity: 10,
          unit: 'אמפולה',
          price: 12,
          expirationDate: '2025-11-15',
          status: 'expiring',
        },
        {
          id: 4,
          name: 'חומר סתימה קומפוזיט',
          category: 'חומרי טיפול',
          quantity: 45,
          minQuantity: 20,
          unit: 'מזרק',
          price: 85,
          status: 'healthy',
        },
        {
          id: 5,
          name: 'מברשות שיניים',
          category: 'מוצרי היגיינה',
          quantity: 120,
          minQuantity: 50,
          unit: 'יחידה',
          price: 8,
          status: 'healthy',
        },
      ];

      // Mock alerts
      const mockAlerts: StockAlert[] = [
        {
          id: 1,
          productName: 'כפפות לטקס',
          currentQty: 5,
          minQty: 20,
          alertType: 'low_stock',
          severity: 'high',
        },
        {
          id: 2,
          productName: 'מסכות כירורגיות',
          currentQty: 15,
          minQty: 30,
          alertType: 'low_stock',
          severity: 'medium',
        },
        {
          id: 3,
          productName: 'אנסתזיה מקומית',
          currentQty: 25,
          minQty: 10,
          alertType: 'expiring',
          severity: 'medium',
        },
      ];

      // Mock valuation
      const mockValuation = {
        totalCost: 125000,
        totalValue: 185000,
        potentialProfit: 60000,
      };

      setInventory(mockInventory);
      setAlerts(mockAlerts);
      setValuation(mockValuation);
    } catch (error) {
      console.error('Error loading inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical':
        return 'error';
      case 'low':
        return 'warning';
      case 'expiring':
        return 'info';
      case 'healthy':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'critical':
        return 'קריטי';
      case 'low':
        return 'נמוך';
      case 'expiring':
        return 'פג תוקף בקרוב';
      case 'healthy':
        return 'תקין';
      default:
        return status;
    }
  };

  const handleCreatePurchaseOrder = () => {
    setPurchaseOrderOpen(true);
  };

  const handleClosePurchaseOrder = () => {
    setPurchaseOrderOpen(false);
    setSelectedItems([]);
  };

  const handleSubmitPurchaseOrder = () => {
    // In real implementation, would create purchase order via API
    console.log('Creating purchase order for items:', selectedItems);
    handleClosePurchaseOrder();
  };

  const criticalItems = inventory.filter(item => item.status === 'critical').length;
  const lowStockItems = inventory.filter(item => item.status === 'low').length;
  const expiringItems = inventory.filter(item => item.status === 'expiring').length;

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, direction: 'rtl' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          <InventoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          ניהול מלאי וציוד
        </Typography>
        <Box>
          <Tooltip title="רענן נתונים">
            <IconButton onClick={loadInventoryData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            color="primary"
            startIcon={<ShoppingCartIcon />}
            onClick={handleCreatePurchaseOrder}
            sx={{ ml: 1 }}
          >
            צור הזמנת רכש
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <AlertTitle>התראות מלאי</AlertTitle>
          יש {alerts.length} פריטים הדורשים תשומת לב: {criticalItems} קריטיים, {lowStockItems} במלאי נמוך, {expiringItems} פגי תוקף בקרוב
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                סה"כ פריטים
              </Typography>
              <Typography variant="h4">{inventory.length}</Typography>
              <Typography variant="body2" color="textSecondary">
                בכל הקטגוריות
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                שווי מלאי
              </Typography>
              <Typography variant="h4">₪{valuation.totalValue.toLocaleString()}</Typography>
              <Typography variant="body2" color="success.main">
                רווח פוטנציאלי: ₪{valuation.potentialProfit.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: 'error.light' }}>
            <CardContent>
              <Typography color="error.contrastText" gutterBottom>
                <WarningIcon sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                פריטים קריטיים
              </Typography>
              <Typography variant="h4" color="error.contrastText">{criticalItems}</Typography>
              <Typography variant="body2" color="error.contrastText">
                דורשים הזמנה מיידית
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: 'info.light' }}>
            <CardContent>
              <Typography color="info.contrastText" gutterBottom>
                <CalendarIcon sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                פגי תוקף בקרוב
              </Typography>
              <Typography variant="h4" color="info.contrastText">{expiringItems}</Typography>
              <Typography variant="body2" color="info.contrastText">
                30 ימים הקרובים
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Inventory Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            רשימת מלאי
          </Typography>
          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>שם הפריט</TableCell>
                  <TableCell>קטגוריה</TableCell>
                  <TableCell align="center">כמות</TableCell>
                  <TableCell align="center">מינימום</TableCell>
                  <TableCell align="center">יחידה</TableCell>
                  <TableCell align="center">מחיר</TableCell>
                  <TableCell align="center">תוקף</TableCell>
                  <TableCell align="center">סטטוס</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inventory.map((item) => (
                  <TableRow
                    key={item.id}
                    sx={{
                      bgcolor: item.status === 'critical' ? 'error.light' : 'inherit',
                      '&:hover': { bgcolor: 'action.hover' },
                    }}
                  >
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.category}</TableCell>
                    <TableCell align="center">
                      <Typography
                        sx={{
                          fontWeight: item.quantity < item.minQuantity ? 'bold' : 'normal',
                          color: item.quantity < item.minQuantity ? 'error.main' : 'inherit',
                        }}
                      >
                        {item.quantity}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">{item.minQuantity}</TableCell>
                    <TableCell align="center">{item.unit}</TableCell>
                    <TableCell align="center">₪{item.price}</TableCell>
                    <TableCell align="center">
                      {item.expirationDate ? (
                        <Typography variant="body2" color="info.main">
                          {new Date(item.expirationDate).toLocaleDateString('he-IL')}
                        </Typography>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={getStatusText(item.status)}
                        color={getStatusColor(item.status) as any}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Purchase Order Dialog */}
      <Dialog open={purchaseOrderOpen} onClose={handleClosePurchaseOrder} maxWidth="md" fullWidth>
        <DialogTitle>יצירת הזמנת רכש</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="ספק"
              variant="outlined"
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              פריטים להזמנה:
            </Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>פריט</TableCell>
                    <TableCell align="center">כמות נוכחית</TableCell>
                    <TableCell align="center">כמות להזמנה</TableCell>
                    <TableCell align="center">מחיר יחידה</TableCell>
                    <TableCell align="center">סה"כ</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {inventory
                    .filter(item => item.status === 'critical' || item.status === 'low')
                    .map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="center">
                          <TextField
                            type="number"
                            size="small"
                            defaultValue={item.minQuantity * 2}
                            sx={{ width: 80 }}
                          />
                        </TableCell>
                        <TableCell align="center">₪{item.price}</TableCell>
                        <TableCell align="center">₪{item.price * item.minQuantity * 2}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePurchaseOrder}>ביטול</Button>
          <Button onClick={handleSubmitPurchaseOrder} variant="contained" color="primary">
            צור הזמנה
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InventoryDashboard;


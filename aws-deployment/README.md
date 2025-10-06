# 🚀 Dental Clinic SaaS - AWS Deployment Guide

## Phase 1: Security & SSL/TLS Setup

This guide will help you set up SSL/TLS encryption and automated backups for your Dental Clinic Odoo instance on AWS.

---

## 📋 Prerequisites

Before starting, ensure you have:

1. ✅ **EC2 Instance** running Ubuntu 22.04
2. ✅ **Odoo 19** installed and running
3. ✅ **Domain name** pointing to your EC2 public IP
4. ✅ **Port 443** open in Security Group
5. ✅ **SSH or Instance Connect** access to EC2

---

## 🔒 Step 1: SSL/TLS Setup

### Option A: Using Domain Name (Recommended)

**Prerequisites:**
- You have a domain name (e.g., `dental.example.com`)
- DNS A record points to your EC2 public IP

**Run:**
```bash
cd /tmp
curl -O https://raw.githubusercontent.com/scubapro711/dental-clinic-ai/v14.0-agent-driven-system/aws-deployment/setup-ssl-tls.sh
chmod +x setup-ssl-tls.sh
sudo ./setup-ssl-tls.sh
```

**Follow the prompts:**
1. Enter your domain name
2. Enter your email address
3. Confirm and wait for installation

**Result:**
- ✅ Nginx installed and configured
- ✅ Let's Encrypt SSL certificate obtained
- ✅ HTTP → HTTPS redirect enabled
- ✅ Auto-renewal configured

---

### Option B: Using IP Address (Testing Only)

If you don't have a domain, you can use a self-signed certificate for testing:

```bash
cd /tmp
curl -O https://raw.githubusercontent.com/scubapro711/dental-clinic-ai/v14.0-agent-driven-system/aws-deployment/setup-ssl-self-signed.sh
chmod +x setup-ssl-self-signed.sh
sudo ./setup-ssl-self-signed.sh
```

⚠️ **Warning:** Self-signed certificates will show browser warnings. Use only for testing!

---

## 💾 Step 2: Automated Backups

**Run:**
```bash
cd /tmp
curl -O https://raw.githubusercontent.com/scubapro711/dental-clinic-ai/v14.0-agent-driven-system/aws-deployment/setup-backups.sh
chmod +x setup-backups.sh
sudo ./setup-backups.sh
```

**Result:**
- ✅ Daily automated backups at 2:00 AM
- ✅ Database + filestore backup
- ✅ 30-day retention policy
- ✅ Backup logs

**Manual backup:**
```bash
sudo /usr/local/bin/odoo-backup.sh
```

**View backups:**
```bash
ls -lh /var/backups/odoo/
```

---

## 🧪 Step 3: Verification

### Test SSL/TLS:
```bash
# Check Nginx status
sudo systemctl status nginx

# Check SSL certificate
sudo certbot certificates

# Test HTTPS connection
curl -I https://your-domain.com
```

### Test Backups:
```bash
# Check backup log
tail -f /var/log/odoo-backup.log

# List backups
ls -lh /var/backups/odoo/

# Check cron job
sudo crontab -l
```

---

## 🔧 Configuration

### Update Odoo Base URL:

1. Login to Odoo as admin
2. Go to **Settings** → **General Settings**
3. Update **System Parameters**:
   - Key: `web.base.url`
   - Value: `https://your-domain.com`

### Nginx Configuration:

Location: `/etc/nginx/sites-available/odoo`

**Reload after changes:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 Monitoring

### Check Odoo Status:
```bash
sudo systemctl status odoo
sudo journalctl -u odoo -f
```

### Check Nginx Logs:
```bash
sudo tail -f /var/log/nginx/odoo-access.log
sudo tail -f /var/log/nginx/odoo-error.log
```

### Check SSL Renewal:
```bash
sudo certbot renew --dry-run
```

---

## 🆘 Troubleshooting

### SSL Certificate Issues:

**Problem:** Certbot fails to obtain certificate

**Solution:**
1. Check DNS: `nslookup your-domain.com`
2. Check port 80 is open: `sudo netstat -tlnp | grep :80`
3. Check Nginx: `sudo nginx -t`
4. Try manual: `sudo certbot --nginx -d your-domain.com`

### Nginx Issues:

**Problem:** 502 Bad Gateway

**Solution:**
1. Check Odoo is running: `sudo systemctl status odoo`
2. Check Odoo port: `sudo netstat -tlnp | grep :8069`
3. Check Nginx config: `sudo nginx -t`
4. Check logs: `sudo tail -f /var/log/nginx/odoo-error.log`

### Backup Issues:

**Problem:** Backup fails

**Solution:**
1. Check disk space: `df -h`
2. Check permissions: `ls -la /var/backups/odoo`
3. Check log: `tail -f /var/log/odoo-backup.log`
4. Run manually: `sudo /usr/local/bin/odoo-backup.sh`

---

## 🔐 Security Checklist

After setup, verify:

- [ ] HTTPS is working
- [ ] HTTP redirects to HTTPS
- [ ] SSL certificate is valid
- [ ] Auto-renewal is enabled
- [ ] Backups are running daily
- [ ] Firewall allows only necessary ports (22, 80, 443)
- [ ] Odoo admin password is strong
- [ ] Database password is strong
- [ ] SSH key authentication is enabled
- [ ] Root login is disabled

---

## 📞 Support

If you encounter issues:

1. Check logs: `/var/log/nginx/` and `/var/log/odoo-backup.log`
2. Review this guide
3. Check Odoo documentation
4. Contact support

---

## ✅ Next Steps

After completing Phase 1:

1. ✅ Test your HTTPS site
2. ✅ Verify backups are working
3. ✅ Update Odoo base URL
4. ✅ Test Agents with real data
5. 🚀 Move to Phase 2: Agent Testing

---

**Created:** October 6, 2025  
**Version:** 1.0  
**Branch:** v14.0-agent-driven-system

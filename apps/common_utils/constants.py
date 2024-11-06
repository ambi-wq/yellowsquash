import datetime

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)

ACCESS = (
    ('all', 'All'),
    ('portal', 'Portal')
)

TITLE_CHOICES = (
    ('Dr', 'Dr'),
    ('Er', 'Er'),
    ('Mr', 'Mr'),
    ('Mrs', 'Mrs'),
    ('Miss', 'Miss'),
    ('Master', 'Master'),
)

TYPE_CHOICES = (
    ('admin', 'Admin'),
    ('customer', 'Customer'),
    ('expert', 'Expert'),
    ('teammember','Team Member')
)

PAYMENT_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
)

SESSION_TYPE = (
    ('permanent', 'Permanent'),
    ('temporary', 'Temporary'),
)

SESSION_SCHEDULE_TYPE = (
    ('daily', 'DAILY'),
    ('once', 'ONCE'),
    ('weekly', 'WEEKLY'),
    ('monthly', 'MONTHLY'),
)

WEEK_DAYS = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)

DAY_OF_MONTH = [(i, i) for i in range(1, 32)]

BATCH_STATUS = (
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('cancelled', 'Cancelled'),
)

BLOG_STATUS = (
    ('draft', 'DRAFT'),
    ('requested', 'REQUESTED'),
    ('approved', 'APPROVED'),
    ('rejected', 'REJECTED'),
    ('published', 'PUBLISHED'),
    ('under_review','UNDER_REVIEW')
)

TAG_STATUS = (
    ('active', 'ACTIVE'),
    ('inactive', 'INACTIVE'),
)

PAYMENT_TYPE = (
    ('bank', 'BANK'),
    ('upi', 'UPI'),
    ('credit card', 'CREDIT CARD'),
    ('netbanking', 'NETBANKING')
)

PAYMENT_STATUS = (
    ('active', 'ACTIVE'),
    ('inactive', 'INACTIVE'),
    ('payment_under_review', 'PAYMENT_UNDER_REVIEW')
)

PRIVACY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private')
)
POST_MODE_CHOICES = (
    ('admin', 'Admin'),
    ('members', 'Members')
)
GROUP_APPROVAL_STATUS = (
    ('pending', 'Pending'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('removed', 'Removed')
)

DEGREE_CHOICES = (
    ('High School', 'High School'), ('Pre University (XII)', 'Pre University (XII)'), ('Diploma', 'Diploma'),
    ("3 Year-Bachelor's Degree", "3 Year-Bachelor's Degree"), ("4 Year-Bachelor's Degree", "4 Year-Bachelor's Degree"),
    ("5 Year-Bachelor's Degree", "5 Year-Bachelor's Degree"), ("Master's Degree", "Master's Degree"),
    ('Doctoral Degree', 'Doctoral Degree'), ('MBBS', 'MBBS'),('Certification','Certification'))


YEAR_CHOICES = [(r,r) for r in range(1984, datetime.date.today().year+1)]


PROGRAM_REVIEW_STATUS = (
    ('approved', 'APPROVED'),
    ('under_review','UNDER_REVIEW')
)

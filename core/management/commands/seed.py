# core/management/commands/seed.py
#
# Usage:
#   python manage.py seed           ← creates all demo data
#   python manage.py seed --clear   ← wipes then re-seeds

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from core.models import (
    LostItem, FoundItem, ContactMessage,
    Review, ReviewReply, ReviewLike,
    Claim, Notification,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Notification.objects.all().delete()
            Claim.objects.all().delete()
            ReviewLike.objects.all().delete()
            ReviewReply.objects.all().delete()
            Review.objects.all().delete()
            ContactMessage.objects.all().delete()
            FoundItem.objects.all().delete()
            LostItem.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('  Done clearing.\n'))

        # ── Users ──────────────────────────────────────────────────────────
        self.stdout.write('    Seeding users...')

        admin = self._make_user(
            username='superadmin',
            email='superadmin@uom.ac.mu',
            password='Admin@1234',
            role='admin',
            first_name='Rachel',
            last_name='Fontaine',
            is_staff=True,
        )

        # Students
        alice = self._make_user(
            username='alice_s',
            email='alice.smith@uom.ac.mu',
            password='Alice@1234',
            role='student',
            first_name='Alice',
            last_name='Smith',
            student_id='S21001',
            phone='59101111',
        )
        ben = self._make_user(
            username='ben_k',
            email='ben.kumar@uom.ac.mu',
            password='Ben@1234',
            role='student',
            first_name='Ben',
            last_name='Kumar',
            student_id='S21002',
            phone='59102222',
        )
        claire = self._make_user(
            username='claire_d',
            email='claire.dubois@uom.ac.mu',
            password='Claire@1234',
            role='student',
            first_name='Claire',
            last_name='Dubois',
            student_id='S21003',
            phone='59103333',
        )

        # Staff
        dr_nair = self._make_user(
            username='dr_nair',
            email='p.nair@uom.ac.mu',
            password='Nair@1234',
            role='staff',
            first_name='Priya',
            last_name='Nair',
            phone='59201111',
        )
        mr_paul = self._make_user(
            username='mr_paul',
            email='t.paul@uom.ac.mu',
            password='Paul@1234',
            role='staff',
            first_name='Thomas',
            last_name='Paul',
            phone='59202222',
        )

        today = date.today()

        # ── Lost Items ─────────────────────────────────────────────────────
        self.stdout.write('\n    Seeding lost items...')

        # pending
        lost1 = self._make_lost(
            alice, 'Black Laptop Bag', 'bags',
            'Left near the library entrance on the bench outside',
            today - timedelta(days=3), 'pending',
        )
        lost2 = self._make_lost(
            alice, 'AirPods Pro (White)', 'electronics',
            'Dropped somewhere in Block A canteen during lunch',
            today - timedelta(days=7), 'pending',
        )
        lost3 = self._make_lost(
            ben, 'Calculus Textbook', 'books_stationery',
            'Left in Lecture Hall 3 after the morning session',
            today - timedelta(days=5), 'pending',
        )
        lost4 = self._make_lost(
            ben, 'Blue Water Bottle', 'other',
            'Sports complex, near the football field',
            today - timedelta(days=2), 'pending',
        )
        lost5 = self._make_lost(
            claire, 'Silver Bracelet', 'accessories',
            'Somewhere between Block B and the student canteen',
            today - timedelta(days=9), 'pending',
        )
        lost6 = self._make_lost(
            claire, 'Prescription Glasses', 'other',
            'Faculty of Science, Room 101 or the corridor outside',
            today - timedelta(days=1), 'pending',
        )
        lost7 = self._make_lost(
            dr_nair, 'Staff ID Card', 'id_cards',
            'Possibly dropped near the Faculty of Engineering office',
            today - timedelta(days=4), 'pending',
        )
        lost8 = self._make_lost(
            mr_paul, 'Car Keys (Toyota, red keyring)', 'keys',
            'Staff car park or main admin building corridor',
            today - timedelta(days=6), 'pending',
        )

        # found (claim submitted, pending review)
        lost9 = self._make_lost(
            alice, 'UoM Student ID Card', 'id_cards',
            'Lost around the Faculty of Engineering reception',
            today - timedelta(days=10), 'found',
        )
        lost10 = self._make_lost(
            ben, 'Black Hoodie (Size M)', 'clothing',
            'Student lounge on the ground floor of Block C',
            today - timedelta(days=12), 'found',
        )

        # resolved
        lost11 = self._make_lost(
            claire, 'Wireless Mouse', 'electronics',
            'Computer lab 3, left on desk after project session',
            today - timedelta(days=20), 'resolved',
        )
        lost12 = self._make_lost(
            dr_nair, 'Umbrella (navy blue)', 'other',
            'Left at the staff common room',
            today - timedelta(days=18), 'resolved',
        )

        # ── Found Items ────────────────────────────────────────────────────
        self.stdout.write('\n    Seeding found items...')

        # pending
        found1 = self._make_found(
            ben, 'Black Leather Wallet', 'accessories',
            'Found near the main gate security desk on the pavement',
            today - timedelta(days=2), 'pending',
        )
        found2 = self._make_found(
            dr_nair, 'Set of Keys (3 keys, blue lanyard)', 'keys',
            'Found on a bench outside Block C lecture rooms',
            today - timedelta(days=4), 'pending',
        )
        found3 = self._make_found(
            claire, 'Scientific Calculator (Casio FX-991)', 'electronics',
            'Found in Lab 204 after the afternoon practical',
            today - timedelta(days=3), 'pending',
        )
        found4 = self._make_found(
            mr_paul, 'Red Jacket (Size L)', 'clothing',
            'Left on a chair in the staff meeting room, Block A',
            today - timedelta(days=7), 'pending',
        )
        found5 = self._make_found(
            alice, 'Earphones (wired, black)', 'electronics',
            'Found on a library desk, floor 2',
            today - timedelta(days=1), 'pending',
        )
        found6 = self._make_found(
            ben, 'Green Pencil Case', 'books_stationery',
            'Found near the vending machines on ground floor',
            today - timedelta(days=5), 'pending',
        )
        found7 = self._make_found(
            claire, 'UoM Student ID Card', 'id_cards',
            'Found in the library reading room between books',
            today - timedelta(days=1), 'pending',
        )
        found8 = self._make_found(
            dr_nair, 'Phone Charger (USB-C)', 'electronics',
            'Left plugged in at a socket in the postgrad lounge',
            today - timedelta(days=8), 'pending',
        )

        # claimed
        found9 = self._make_found(
            mr_paul, 'Prescription Glasses (black frame)', 'accessories',
            'Found on the staircase between floors 1 and 2, Block B',
            today - timedelta(days=11), 'claimed',
        )
        found10 = self._make_found(
            alice, 'Laptop Power Adapter (Dell)', 'electronics',
            'Found near a charging station in the student lounge',
            today - timedelta(days=9), 'claimed',
        )

        # resolved
        found11 = self._make_found(
            ben, 'Black Backpack (Adidas)', 'bags',
            'Found outside the canteen near the recycling bins',
            today - timedelta(days=22), 'resolved',
        )
        found12 = self._make_found(
            claire, 'Student Bus Pass', 'id_cards',
            'Found on a seat in Lecture Theatre 1',
            today - timedelta(days=19), 'resolved',
        )
        found13 = self._make_found(
            dr_nair, 'Silver Ring', 'accessories',
            'Found on the floor of the ladies bathroom, Block A',
            today - timedelta(days=25), 'resolved',
        )

        # ── Claims ─────────────────────────────────────────────────────────
        self.stdout.write('\n    Seeding claims...')

        # pending claims
        self._make_claim(
            ben, None, found9,
            'Those are my glasses — black rectangular frame with a small scratch on the left arm.',
            'pending',
        )
        self._make_claim(
            claire, None, found10,
            'I lost my Dell adapter last week. The brick has a sticker with my student ID S21003.',
            'pending',
        )
        self._make_claim(
            alice, lost9, None,
            'That is my ID card. My photo and student number S21001 should be on it.',
            'pending',
        )
        self._make_claim(
            ben, lost10, None,
            'I lost a black hoodie around that time. Mine has a small bleach stain on the left sleeve.',
            'pending',
        )

        # returned
        self._make_claim(
            claire, lost11, None,
            'My wireless mouse, I left it in the lab after the group project.',
            'returned',
        )
        self._make_claim(
            dr_nair, lost12, None,
            'That is my navy umbrella, I left it in the common room on Tuesday.',
            'returned',
        )
        self._make_claim(
            alice, None, found11,
            'Black Adidas backpack is mine — has my initials A.S. written inside the top pocket.',
            'returned',
        )
        self._make_claim(
            claire, None, found12,
            'That is my bus pass, my name Claire Dubois and photo are on it.',
            'returned',
        )
        self._make_claim(
            alice, None, found13,
            'The silver ring belongs to me, it has an engraving inside that reads "forever".',
            'returned',
        )

        # rejected
        self._make_claim(
            ben, None, found3,
            'I think I left my calculator there but I am not 100% sure of the model.',
            'rejected',
        )
        self._make_claim(
            mr_paul, None, found1,
            'Could be my wallet, I lost one last week around that area.',
            'rejected',
        )

        # ── Reviews ────────────────────────────────────────────────────────
        self.stdout.write('\n    Seeding reviews...')

        r1 = self._make_review(
            alice, 5,
            'UniFind is fantastic! I reported my lost bag and got a claim within a day. '
            'The interface is clean and easy to use. Every university should have this.',
        )
        r2 = self._make_review(
            ben, 4,
            'Really helpful platform. Found my wallet thanks to someone who posted it here. '
            'Would love a mobile app version though — browsing on phone could be smoother.',
        )
        r3 = self._make_review(
            claire, 5,
            'I was stressed about losing my glasses before an exam and UniFind saved me. '
            'The claim process is straightforward and the admin team is responsive.',
        )
        r4 = self._make_review(
            dr_nair, 4,
            'As a staff member I use this regularly. Logging found items is quick. '
            'A notification when a claim is resolved would be a great addition.',
        )
        r5 = self._make_review(
            mr_paul, 3,
            'Decent platform but search could be more powerful. '
            'I want to filter by building or block, not just category.',
        )

        # Banned reviews
        r6 = self._make_review(
            ben, 1,
            'SCAM SITE!!! I submitted a claim and they asked me to pay to get my item back. '
            'Avoid this platform completely!!!!',
            is_banned=True,
            ban_reason='False and misleading claim. UniFind never charges users.',
        )
        r7 = self._make_review(
            claire, 2,
            'Useless. My item was stolen by whoever "found" it and nothing was done. '
            'The admins do not care at all about students.',
            is_banned=True,
            ban_reason='Unverified accusation. User did not follow up through proper channels.',
        )

        # Admin replies
        ReviewReply.objects.create(
            review=r1, admin=admin,
            comment='Thank you so much Alice! We are thrilled UniFind could help. '
                    'Your feedback motivates us to keep improving. 😊',
        )
        ReviewReply.objects.create(
            review=r2, admin=admin,
            comment='Thanks Ben! A mobile-friendly update is on our roadmap — stay tuned!',
        )
        ReviewReply.objects.create(
            review=r4, admin=admin,
            comment='Great suggestion Dr. Nair! Claim resolution notifications are planned for the next release.',
        )
        ReviewReply.objects.create(
            review=r5, admin=admin,
            comment='Noted Thomas! Location-based filtering is something we are actively working on.',
        )

        # Likes
        for review, likers in [
            (r1, [ben, claire, dr_nair, mr_paul]),
            (r2, [alice, claire]),
            (r3, [alice, ben, mr_paul]),
            (r4, [alice, claire]),
            (r5, [ben]),
        ]:
            for liker in likers:
                ReviewLike.objects.get_or_create(review=review, user=liker)

        # ── Contact Messages ───────────────────────────────────────────────
        self.stdout.write('\n    Seeding contact messages...')

        ContactMessage.objects.create(
            name='Alice Smith', email='alice.smith@uom.ac.mu',
            subject='Question about my pending claim',
            message='Hi, I submitted a claim 3 days ago on a lost ID card but have not received any update. '
                    'Could you please check the status? My student ID is S21001. Thank you.',
            user=alice,
        )
        ContactMessage.objects.create(
            name='Ben Kumar', email='ben.kumar@uom.ac.mu',
            subject='Unable to upload photo for found item',
            message='I am trying to upload a photo when reporting a found item but the upload keeps failing. '
                    'It is a JPEG file around 2MB. Is there a file size limit? Please advise.',
            user=ben,
        )
        ContactMessage.objects.create(
            name='Anonymous', email='student.anon@uom.ac.mu',
            subject='Found a phone near canteen',
            message='I found a phone near the canteen this morning but could not find a suitable category. '
                    'What should I select for a mobile phone? Also, where do I hand it in physically?',
        )
        ContactMessage.objects.create(
            name='Thomas Paul', email='t.paul@uom.ac.mu',
            subject='Request to add a new category',
            message='Could you consider adding a "Sports Equipment" category? '
                    'We often find items like water bottles, shin guards and gym gear that do not fit well '
                    'into the existing options.',
            user=mr_paul,
        )
        ContactMessage.objects.create(
            name='Priya Nair', email='p.nair@uom.ac.mu',
            subject='Item still showing as pending after resolution',
            message='An item I reported as found was claimed and returned last week but it still shows '
                    '"pending" in my profile. Could someone update the status on the backend?',
            user=dr_nair, is_read=True,
        )

        # ── Summary ────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n✅  Seeding complete!\n'))
        self.stdout.write(self.style.HTTP_INFO('━' * 52))
        self.stdout.write(self.style.HTTP_INFO('  USER ACCOUNTS'))
        self.stdout.write(self.style.HTTP_INFO('━' * 52))
        self.stdout.write(f"  {'Username':<16} {'Password':<16} {'Role'}")
        self.stdout.write('  ' + '─' * 48)
        accounts = [
            ('superadmin', 'Admin@1234',  'admin'),
            ('alice_s',    'Alice@1234',  'student'),
            ('ben_k',      'Ben@1234',    'student'),
            ('claire_d',   'Claire@1234', 'student'),
            ('dr_nair',    'Nair@1234',   'staff'),
            ('mr_paul',    'Paul@1234',   'staff'),
        ]
        for username, password, role in accounts:
            self.stdout.write(f"  {username:<16} {password:<16} {role}")
        self.stdout.write(self.style.HTTP_INFO('━' * 52))
        self.stdout.write('')

    # ── Helpers ────────────────────────────────────────────────────────────

    def _make_user(self, username, email, password, role,
                   first_name='', last_name='',
                   student_id='', phone='', is_staff=False):
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'  ⚠  "{username}" already exists — skipping.')
            return User.objects.get(username=username)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            role=role, first_name=first_name, last_name=last_name,
            student_id=student_id, phone=phone, is_staff=is_staff,
        )
        self.stdout.write(f'  ✓  {role:<8} {username}')
        return user

    def _make_lost(self, user, item_name, category, last_seen, date_lost, status='pending'):
        item = LostItem.objects.create(
            user=user, item_name=item_name, category=category,
            description=(
                f'{item_name} — reported missing by {user.get_full_name() or user.username}. '
                f'If found please submit a claim or contact us.'
            ),
            last_seen=last_seen, date_lost=date_lost, status=status,
        )
        self.stdout.write(f'  ✓  [{status:<8}] Lost:  {item_name}')
        return item

    def _make_found(self, user, item_name, category, found_at, date_found, status='pending'):
        item = FoundItem.objects.create(
            user=user, item_name=item_name, category=category,
            description=(
                f'{item_name} — reported found by {user.get_full_name() or user.username}. '
                f'Submit a claim with proof of ownership to retrieve it.'
            ),
            found_at=found_at, date_found=date_found, status=status,
        )
        self.stdout.write(f'  ✓  [{status:<8}] Found: {item_name}')
        return item

    def _make_claim(self, claimer, lost_item, found_item, details, status='pending'):
        # Create with default 'pending' first (avoids double-firing Claim.save signals)
        claim = Claim.objects.create(
            claimer=claimer,
            lost_item=lost_item,
            found_item=found_item,
            details=details,
        )
        # Then force the desired status + matching item status via update()
        if status != 'pending':
            Claim.objects.filter(pk=claim.pk).update(status=status)
            item = lost_item or found_item
            if status == 'returned':
                type(item).objects.filter(pk=item.pk).update(status='resolved')
            elif status == 'rejected':
                type(item).objects.filter(pk=item.pk).update(status='pending')

        item = lost_item or found_item
        self.stdout.write(
            f'  ✓  [{status:<8}] Claim by {claimer.username} → {item.item_name}'
        )
        return claim

    def _make_review(self, user, rating, comment, is_banned=False, ban_reason=''):
        review = Review.objects.create(
            user=user, rating=rating, comment=comment,
            is_banned=is_banned, ban_reason=ban_reason,
        )
        label = 'BANNED' if is_banned else f'{"★" * rating}'
        self.stdout.write(f'  ✓  {label:<10} Review by {user.username}')
        return review
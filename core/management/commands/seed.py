# core/management/commands/seed.py
#
# Usage:
#   python manage.py seed           ← creates all demo data
#   python manage.py seed --clear   ← wipes then re-seeds

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import date, timedelta
from core.models import (
    LostItem, FoundItem, ContactMessage,
    Review, ReviewReply, ReviewLike,
    Claim, Notification,
    fire_match_notifications,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo data using local media files'

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
        self.stdout.write('Seeding users...')

        admin = self._make_user(
            'superadmin', 'superadmin@uom.ac.mu', 'Admin@1234', 'admin',
            first_name='Rachel', last_name='Fontaine', is_staff=True,
        )
        alice = self._make_user(
            'alice_s', 'alice.smith@uom.ac.mu', 'Alice@1234', 'student',
            first_name='Alice', last_name='Smith', student_id='S21001', phone='59101111',
        )
        ben = self._make_user(
            'ben_k', 'ben.kumar@uom.ac.mu', 'Ben@1234', 'student',
            first_name='Ben', last_name='Kumar', student_id='S21002', phone='59102222',
        )
        claire = self._make_user(
            'claire_d', 'claire.dubois@uom.ac.mu', 'Claire@1234', 'student',
            first_name='Claire', last_name='Dubois', student_id='S21003', phone='59103333',
        )
        dr_nair = self._make_user(
            'dr_nair', 'p.nair@uom.ac.mu', 'Nair@1234', 'staff',
            first_name='Priya', last_name='Nair', phone='59201111',
        )
        mr_paul = self._make_user(
            'mr_paul', 't.paul@uom.ac.mu', 'Paul@1234', 'staff',
            first_name='Thomas', last_name='Paul', phone='59202222',
        )

        today = date.today()

        # ══════════════════════════════════════════════════════════════════
        # LOST ITEMS  (the "older" posts — seeded first)
        # ══════════════════════════════════════════════════════════════════
        self.stdout.write('\nSeeding lost items...')

        # ── General pending (no match counterpart) ────────────────────────
        lost_bag      = self._make_lost(alice,   'Black Laptop Bag',            'bags',            'Left near the library entrance on the bench outside',            today - timedelta(days=3),  'pending')
        lost_airpods  = self._make_lost(alice,   'AirPods Pro White',           'electronics',     'Dropped somewhere in Block A canteen during lunch',              today - timedelta(days=7),  'pending')
        lost_calc_txt = self._make_lost(ben,     'Calculus Textbook',           'books_stationery','Left in Lecture Hall 3 after the morning session',               today - timedelta(days=5),  'pending')
        lost_bottle   = self._make_lost(ben,     'Blue Water Bottle',           'other',           'Sports complex near the football field',                         today - timedelta(days=2),  'pending')
        lost_glasses  = self._make_lost(claire,  'Prescription Glasses',        'other',           'Faculty of Science Room 101 or the corridor outside',           today - timedelta(days=1),  'pending')
        lost_staff_id = self._make_lost(dr_nair, 'Staff ID Card',               'id_cards',        'Possibly dropped near the Faculty of Engineering office',        today - timedelta(days=4),  'pending')
        lost_car_keys = self._make_lost(mr_paul, 'Car Keys Toyota Red Keyring', 'keys',            'Staff car park or main admin building corridor',                today - timedelta(days=6),  'pending')

        # ── MATCH PAIR A — Alice lost bracelet at library (9 days ago) ────
        #    Ben will post finding a bracelet at the library today → alice gets match notif
        lost_bracelet = self._make_lost(
            alice, 'Silver Bracelet', 'accessories',
            'Library reading room near the study desks on floor 2',
            today - timedelta(days=9), 'pending',
        )

        # ── MATCH PAIR B — Alice lost earphones at canteen (5 days ago) ──
        #    Claire will post finding earphones at the canteen today → alice gets match notif
        lost_earphones = self._make_lost(
            alice, 'Earphones Wired Black', 'electronics',
            'Block A canteen left on a table near the window',
            today - timedelta(days=5), 'pending',
        )

        # ── MATCH PAIR C — Claire lost student ID at canteen (6 days ago) ─
        #    Dr Nair will post finding a student ID at the canteen → claire gets match notif
        lost_id = self._make_lost(
            claire, 'Student ID Card', 'id_cards',
            'Block A canteen possibly fell near the serving counter',
            today - timedelta(days=6), 'pending',
        )

        # ── MATCH PAIR D — Mr Paul lost keys near car park (4 days ago) ──
        #    Ben will post finding keys at the car park → mr_paul gets match notif
        lost_keys = self._make_lost(
            mr_paul, 'Toyota Car Keys', 'keys',
            'Staff car park next to the main admin building',
            today - timedelta(days=4), 'pending',
        )

        # ── Claim-status items ────────────────────────────────────────────
        lost_id_uom   = self._make_lost(ben,     'UoM Student ID Card',         'id_cards',        'Lost around the Faculty of Engineering reception',              today - timedelta(days=10), 'found')
        lost_hoodie   = self._make_lost(claire,  'Black Hoodie Size M',         'clothing',        'Student lounge on the ground floor of Block C',                today - timedelta(days=12), 'found')
        lost_mouse    = self._make_lost(claire,  'Wireless Mouse',              'electronics',     'Computer lab 3 left on desk after project session',            today - timedelta(days=20), 'resolved')
        lost_umbrella = self._make_lost(dr_nair, 'Umbrella Navy Blue',          'other',           'Left at the staff common room',                                today - timedelta(days=18), 'resolved')

        # ══════════════════════════════════════════════════════════════════
        # FOUND ITEMS  (unmatched — seeded before match pairs)
        # ══════════════════════════════════════════════════════════════════
        self.stdout.write('\nSeeding found items (unmatched)...')

        found_wallet  = self._make_found(ben,     'Black Leather Wallet',             'accessories',     'Found near the main gate security desk on the pavement',       today - timedelta(days=2),  'pending')
        found_keyset  = self._make_found(dr_nair, 'Set Of Keys Blue Lanyard',         'keys',            'Found on a bench outside Block C lecture rooms',              today - timedelta(days=4),  'pending')
        found_casio   = self._make_found(claire,  'Scientific Calculator Casio',      'electronics',     'Found in Lab 204 after the afternoon practical',              today - timedelta(days=3),  'pending')
        found_jacket  = self._make_found(mr_paul, 'Red Jacket Size L',                'clothing',        'Left on a chair in the staff meeting room Block A',           today - timedelta(days=7),  'pending')
        found_pencil  = self._make_found(ben,     'Green Pencil Case',                'books_stationery','Found near the vending machines on ground floor',             today - timedelta(days=5),  'pending')
        found_charger = self._make_found(dr_nair, 'Phone Charger USB C',              'electronics',     'Left plugged in at a socket in the postgrad lounge',          today - timedelta(days=8),  'pending')

        found_glasses = self._make_found(mr_paul, 'Prescription Glasses Black Frame', 'accessories',     'Found on the staircase between floors 1 and 2 Block B',       today - timedelta(days=11), 'claimed')
        found_adapter = self._make_found(alice,   'Laptop Power Adapter Dell',        'electronics',     'Found near a charging station in the student lounge',         today - timedelta(days=9),  'claimed')

        found_backpack = self._make_found(ben,    'Black Backpack Adidas',            'bags',            'Found outside the canteen near the recycling bins',           today - timedelta(days=22), 'resolved')
        found_buspass = self._make_found(claire,  'Student Bus Pass',                 'id_cards',        'Found on a seat in Lecture Theatre 1',                        today - timedelta(days=19), 'resolved')
        found_ring    = self._make_found(dr_nair, 'Silver Ring',                      'accessories',     'Found on the floor of the ladies bathroom Block A',           today - timedelta(days=25), 'resolved')

        # ══════════════════════════════════════════════════════════════════
        # MATCH PAIRS — "newer" found items posted TODAY
        # Each triggers fire_match_notifications, producing 2 notifications
        # (one to the finder, one to the original loser)
        # ══════════════════════════════════════════════════════════════════
        self.stdout.write('\nSeeding match-trigger found items...')

        # Pair A: Ben finds bracelet at library → alice gets "might be yours"
        #         Ben gets "might belong to someone"
        found_bracelet = self._make_found(
            ben, 'Silver Bracelet', 'accessories',
            'Found on a study desk at the library floor 2',
            today, 'pending',
        )
        self._fire_match(found_bracelet, 'found')

        # Pair B: Claire finds earphones at canteen → alice gets "might be yours"
        #         Claire gets "might belong to someone"
        found_earphones = self._make_found(
            claire, 'Earphones Wired Black', 'electronics',
            'Found on a table in Block A canteen near the window',
            today, 'pending',
        )
        self._fire_match(found_earphones, 'found')

        # Pair C: Dr Nair finds student ID at canteen → claire gets "might be yours"
        #         Dr Nair gets "might belong to someone"
        found_id = self._make_found(
            dr_nair, 'Student ID Card', 'id_cards',
            'Found on a table in Block A canteen near the serving area',
            today, 'pending',
        )
        self._fire_match(found_id, 'found')

        # Pair D: Ben finds Toyota keys at car park → mr_paul gets "might be yours"
        #         Ben gets "might belong to someone"
        found_keys = self._make_found(
            ben, 'Toyota Car Keys', 'keys',
            'Found on the ground in the staff car park beside Block A',
            today, 'pending',
        )
        self._fire_match(found_keys, 'found')

        # ── Claims ─────────────────────────────────────────────────────────
        self.stdout.write('\nSeeding claims...')

        # ben claims glasses (found by mr_paul) → mr_paul gets notif
        self._make_claim(ben,     None,         found_glasses,  'Those are my glasses — black rectangular frame with a small scratch on the left arm.',       'pending')
        # claire claims adapter (found by alice) → alice gets "new claim on your found item"
        self._make_claim(claire,  None,         found_adapter,  'I lost my Dell adapter last week. The brick has a sticker with my student ID S21003.',        'pending')
        # alice claims ben's lost UoM ID → ben gets notif
        self._make_claim(alice,   lost_id_uom,  None,           'I found this ID card near the engineering block — submitting on behalf of the owner.',         'pending')
        # dr_nair claims claire's lost hoodie → claire gets notif
        self._make_claim(dr_nair, lost_hoodie,  None,           'I believe this is the hoodie left in the lounge — black size M with a logo on the chest.',     'pending')

        # Resolved claims
        self._make_claim(alice,   lost_mouse,   None,           'My wireless mouse, I left it in the lab after the group project.',                             'returned')
        self._make_claim(ben,     lost_umbrella,None,           'That is the navy umbrella from the common room — mine has a broken tip on the handle.',        'returned')
        self._make_claim(alice,   None,         found_backpack, 'Black Adidas backpack is mine — has my initials A.S. written inside the top pocket.',          'returned')
        self._make_claim(claire,  None,         found_buspass,  'That is my bus pass, my name Claire Dubois and photo are on it.',                              'returned')
        self._make_claim(alice,   None,         found_ring,     'The silver ring belongs to me, it has an engraving inside that reads "forever".',              'returned')

        # Rejected claims
        self._make_claim(ben,     None,         found_casio,    'I think I left my calculator there but I am not 100% sure of the model.',                      'rejected')
        self._make_claim(mr_paul, None,         found_wallet,   'Could be my wallet, I lost one last week around that area.',                                   'rejected')

        # ── Reviews ────────────────────────────────────────────────────────
        self.stdout.write('\nSeeding reviews...')

        r1 = self._make_review(alice,   5, 'UniFind is fantastic! I reported my lost bag and got a claim within a day. The interface is clean and easy to use. Every university should have this.')
        r2 = self._make_review(ben,     4, 'Really helpful platform. Found my wallet thanks to someone who posted it here. Would love a mobile app version though — browsing on phone could be smoother.')
        r3 = self._make_review(claire,  5, 'I was stressed about losing my glasses before an exam and UniFind saved me. The claim process is straightforward and the admin team is responsive.')
        r4 = self._make_review(dr_nair, 4, 'As a staff member I use this regularly. The new match notification is a brilliant touch — I got alerted the moment someone found an item matching mine!')
        r5 = self._make_review(mr_paul, 3, 'Decent platform but search could be more powerful. I want to filter by building or block, not just category.')

        r6 = self._make_review(ben,   1, 'SCAM SITE!!! I submitted a claim and they asked me to pay to get my item back. Avoid this platform completely!!!!',
                                is_banned=True, ban_reason='False and misleading claim. UniFind never charges users.')
        r7 = self._make_review(claire, 2, 'Useless. My item was stolen by whoever "found" it and nothing was done. The admins do not care at all about students.',
                                is_banned=True, ban_reason='Unverified accusation. User did not follow up through proper channels.')

        ReviewReply.objects.create(review=r1, admin=admin,
            comment='Thank you so much Alice! We are thrilled UniFind could help. Your feedback motivates us to keep improving. 😊')
        ReviewReply.objects.create(review=r2, admin=admin,
            comment='Thanks Ben! A mobile-friendly update is on our roadmap — stay tuned!')
        ReviewReply.objects.create(review=r4, admin=admin,
            comment='So glad the match notifications are working for you Dr. Nair! That feature was built exactly for moments like yours.')
        ReviewReply.objects.create(review=r5, admin=admin,
            comment='Noted Thomas! Location-based filtering is something we are actively working on.')

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
        self.stdout.write('\nSeeding contact messages...')

        ContactMessage.objects.create(
            name='Alice Smith', email='alice.smith@uom.ac.mu',
            subject='Question about my pending claim',
            message='Hi, I submitted a claim 3 days ago on a lost ID card but have not received any update. Could you please check the status? My student ID is S21001. Thank you.',
            user=alice,
        )
        ContactMessage.objects.create(
            name='Ben Kumar', email='ben.kumar@uom.ac.mu',
            subject='Unable to upload photo for found item',
            message='I am trying to upload a photo when reporting a found item but the upload keeps failing. It is a JPEG file around 2MB. Is there a file size limit? Please advise.',
            user=ben,
        )
        ContactMessage.objects.create(
            name='Anonymous', email='student.anon@uom.ac.mu',
            subject='Found a phone near canteen',
            message='I found a phone near the canteen this morning but could not find a suitable category. What should I select for a mobile phone? Also, where do I hand it in physically?',
        )
        ContactMessage.objects.create(
            name='Thomas Paul', email='t.paul@uom.ac.mu',
            subject='Request to add a new category',
            message='Could you consider adding a "Sports Equipment" category? We often find items like water bottles, shin guards and gym gear that do not fit well into the existing options.',
            user=mr_paul,
        )
        ContactMessage.objects.create(
            name='Priya Nair', email='p.nair@uom.ac.mu',
            subject='Item still showing as pending after resolution',
            message='An item I reported as found was claimed and returned last week but it still shows "pending" in my profile. Could someone update the status on the backend?',
            user=dr_nair, is_read=True,
        )

        # ── Summary ────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!\n'))
        self.stdout.write(self.style.HTTP_INFO('━' * 56))
        self.stdout.write(self.style.HTTP_INFO('  USER ACCOUNTS'))
        self.stdout.write(self.style.HTTP_INFO('━' * 56))
        self.stdout.write(f"  {'Username':<16} {'Password':<16} {'Role'}")
        self.stdout.write('  ' + '─' * 52)
        for username, password, role in [
            ('superadmin', 'Admin@1234',  'admin'),
            ('alice_s',    'Alice@1234',  'student'),
            ('ben_k',      'Ben@1234',    'student'),
            ('claire_d',   'Claire@1234', 'student'),
            ('dr_nair',    'Nair@1234',   'staff'),
            ('mr_paul',    'Paul@1234',   'staff'),
        ]:
            self.stdout.write(f"  {username:<16} {password:<16} {role}")
        self.stdout.write(self.style.HTTP_INFO('━' * 56))

        self.stdout.write(self.style.HTTP_INFO('\n  EXPECTED NOTIFICATIONS PER USER'))
        self.stdout.write(self.style.HTTP_INFO('━' * 56))
        rows = [
            ('alice_s',  '🔀 Bracelet match (Ben found yours at library)'),
            ('alice_s',  '🔀 Earphones match (Claire found yours at canteen)'),
            ('alice_s',  '🔔 New claim on found_adapter (by claire)'),
            ('alice_s',  '🔔 New claim on found_backpack → returned'),
            ('alice_s',  '🔔 New claim on found_ring → returned'),
            ('ben_k',    '🔀 Bracelet match (you found it — might belong to someone)'),
            ('ben_k',    '🔀 Keys match (you found them — might belong to someone)'),
            ('ben_k',    '🔔 New claim on lost_id_uom (by alice)'),
            ('claire_d', '🔀 ID card match (Dr Nair found yours at canteen)'),
            ('claire_d', '🔀 Earphones match (you found them — might belong to someone)'),
            ('claire_d', '🔔 New claim on lost_hoodie (by dr_nair)'),
            ('claire_d', '🔔 New claim on found_buspass → returned'),
            ('dr_nair',  '🔀 ID card match (you found it — might belong to someone)'),
            ('dr_nair',  '🔔 New claim on found_ring → returned'),
            ('dr_nair',  '🔔 New claim on lost_umbrella (by ben) → returned'),
            ('mr_paul',  '🔀 Keys match (Ben found yours at car park)'),
            ('mr_paul',  '🔔 New claim on found_glasses (by ben)'),
        ]
        for user, notif in rows:
            self.stdout.write(f"  {user:<12} {notif}")
        self.stdout.write(self.style.HTTP_INFO('━' * 56))
        self.stdout.write('')

    # ── Helpers ────────────────────────────────────────────────────────────

    def _make_user(self, username, email, password, role,
                   first_name='', last_name='', student_id='', phone='', is_staff=False):
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

    def _get_image_path(self, item_name, folder):
        clean = (
            item_name.lower()
            .replace(' ', '_')
            .replace('(', '').replace(')', '')
            .replace(',', '').replace('-', '_')
        )
        filename  = f'{clean}.png'
        rel_path  = os.path.join(folder, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        if os.path.exists(full_path):
            return rel_path
        return None

    def _make_lost(self, user, item_name, category, last_seen, date_lost, status='pending'):
        img = self._get_image_path(item_name, 'lost_items')
        item = LostItem.objects.create(
            user=user, item_name=item_name, category=category,
            description=(
                f'{item_name} — reported missing by {user.get_full_name() or user.username}. '
                f'If found please submit a claim or contact us.'
            ),
            last_seen=last_seen, date_lost=date_lost, status=status,
            photo=img or '',
        )
        icon = '🖼 ' if img else '   '
        self.stdout.write(f'  ✓ {icon}[{status:<8}] Lost:  {item_name}')
        return item

    def _make_found(self, user, item_name, category, found_at, date_found, status='pending'):
        img = self._get_image_path(item_name, 'found_items')
        item = FoundItem.objects.create(
            user=user, item_name=item_name, category=category,
            description=(
                f'{item_name} — reported found by {user.get_full_name() or user.username}. '
                f'Submit a claim with proof of ownership to retrieve it.'
            ),
            found_at=found_at, date_found=date_found, status=status,
            photo=img or '',
        )
        icon = '🖼 ' if img else '   '
        self.stdout.write(f'  ✓ {icon}[{status:<8}] Found: {item_name}')
        return item

    def _fire_match(self, item, item_type):
        """Call fire_match_notifications and log how many notifications were created."""
        before = Notification.objects.filter(notification_type='match').count()
        fire_match_notifications(item, item_type)
        after  = Notification.objects.filter(notification_type='match').count()
        new    = after - before
        if new:
            self.stdout.write(self.style.SUCCESS(
                f'    🔔 {new} match notification(s) fired for "{item.item_name}"'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'    ⚠  0 match notifications fired for "{item.item_name}" — check locations/category'
            ))

    def _make_claim(self, claimer, lost_item, found_item, details, status='pending'):
        claim = Claim.objects.create(
            claimer=claimer,
            lost_item=lost_item,
            found_item=found_item,
            details=details,
        )
        if status != 'pending':
            Claim.objects.filter(pk=claim.pk).update(status=status)
            item = lost_item or found_item
            if status == 'returned':
                type(item).objects.filter(pk=item.pk).update(status='resolved')
            elif status == 'rejected':
                type(item).objects.filter(pk=item.pk).update(status='pending')
        item = lost_item or found_item
        self.stdout.write(f'  ✓  [{status:<8}] Claim by {claimer.username} → {item.item_name}')
        return claim

    def _make_review(self, user, rating, comment, is_banned=False, ban_reason=''):
        review = Review.objects.create(
            user=user, rating=rating, comment=comment,
            is_banned=is_banned, ban_reason=ban_reason,
        )
        label = '🚫 BANNED' if is_banned else '★' * rating
        self.stdout.write(f'  ✓  {label:<10} Review by {user.username}')
        return review
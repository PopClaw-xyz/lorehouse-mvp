"""Protocol model assertions, never live server/database acceptance."""
import json
from pathlib import Path
import unittest
from dataclasses import FrozenInstanceError
from log_model import Referee, LogIdentity
from public_baseline import ENVELOPE_BASELINE

V=json.loads((Path(__file__).resolve().parent.parent/'fixtures/public-baseline.json').read_text())
RAW={r['name']:bytes.fromhex(r['wire_hex']) for r in V['wire']}
GOOD=RAW['opaque_unknown_legal_business']
BAD=RAW['reserved_profile_empty']


class LogSemantics(unittest.TestCase):
    def house(self):
        h=Referee();log=h.create('log-1');h.prepare(log);h.activate(log)
        return h,log

    def test_rejection_precedes_visible_sequence_allocation(self):
        h,log=self.house()
        self.assertEqual(h.admit(GOOD),1)
        with self.assertRaises(ValueError): h.admit(BAD)
        self.assertEqual(h.admit(RAW['profile_supported']),2)
        self.assertEqual(log.rows,[GOOD,RAW['profile_supported']])
        self.assertEqual(h.admit(GOOD),1)

    def test_existing_N_blocks_readiness_and_buffered_delivery(self):
        for legacy in [False,True]:
            with self.subTest(legacy=legacy):
                h,log=self.house();log.rows=[GOOD,BAD,GOOD]
                with self.assertRaises(ValueError): h.prepare(log)
                self.assertFalse(log.ready)
                with self.assertRaisesRegex(ValueError,'PUBLIC_STREAM_UNAVAILABLE'): h.select(log.identity)
                # Inject a readiness/read race to test runtime encounter behavior.
                log.ready=True;c=h.select(log.identity,legacy=legacy);c.page()
                self.assertEqual(c.emitted,[]);self.assertEqual(c.public_after,0)
                self.assertEqual(c.checkpoints,[]);self.assertTrue(c.closed)
                if legacy: self.assertIsNone(c.gap)
                else: self.assertEqual(c.gap,{'reason':'public_log_invalid','lane':'public'})

    def test_prior_page_durable_cursor_survives_gap_and_reconnect(self):
        h,log=self.house();log.rows=[GOOD,BAD,GOOD]
        c=h.select(log.identity);c.page(1);c.page(1)
        self.assertEqual([seq for seq,_ in c.emitted],[1]);self.assertEqual(c.public_after,1)
        retry=h.select(log.identity,public_after=c.public_after);retry.page()
        self.assertTrue(retry.closed);self.assertEqual(retry.public_after,1)
        self.assertEqual(retry.checkpoints,[])

    def test_unclassifiable_scope_only_row_cannot_be_filtered_away(self):
        h,log=self.house();log.rows=[GOOD,BAD,GOOD]
        c=h.select(log.identity,public_after=None,scopes={'abcd':0});c.page()
        self.assertEqual(c.scopes,{'abcd':0})
        self.assertEqual(c.gap,{'reason':'public_log_invalid','lane':'connection'})

    def test_baseline_metadata_is_immutable(self):
        _,log=self.house()
        with self.assertRaises(FrozenInstanceError): log.identity.baseline='wider'

    def test_bidirectional_transition_never_reuses_id_and_fences_old_work(self):
        h,old=self.house();h.admit(GOOD);c=h.select(old.identity);c.page()
        unchanged=(h.server_incarnation,h.server_key,h.session,h.policy)
        wider=h.create('log-2','wider-envelope');h.prepare(wider);h.activate(wider)
        with self.assertRaisesRegex(ValueError,'SELECTION_FENCED'): c.checkpoint()
        self.assertEqual(c.checkpoints,[])
        with self.assertRaisesRegex(ValueError,'LOG_ID_REUSE'): h.create('log-1')
        with self.assertRaisesRegex(ValueError,'LOG_ID_REUSE'): h.activate(old)
        rollback=h.create('log-3');h.prepare(rollback);h.activate(rollback)
        self.assertNotEqual(rollback.identity,old.identity)
        self.assertEqual((h.server_incarnation,h.server_key,h.session,h.policy),unchanged)
        with self.assertRaisesRegex(ValueError,'log_incarnation_changed'): h.select(old.identity)
        fresh=h.select(rollback.identity);self.assertEqual(fresh.public_after,0)

    def test_same_log_restart_keeps_identity_and_cursor(self):
        h,log=self.house();h.admit(GOOD);c=h.select(log.identity);c.page();c.checkpoint()
        h.activate(log);resumed=h.select(log.identity,public_after=c.public_after)
        resumed.page();resumed.checkpoint();self.assertEqual(resumed.public_after,1)
        self.assertEqual(resumed.emitted,[])

    def test_changed_signed_declaration_cannot_rebind_actual_log(self):
        h,log=self.house()
        with self.assertRaisesRegex(ValueError,'log_incarnation_changed'):
            h.select(LogIdentity(log.identity.log,'wider-envelope'))

    def test_explicit_legacy_checks_reserved_even_without_new_declaration(self):
        h=Referee();old=h.create('legacy-log','wider-envelope');h.prepare(old);h.activate(old)
        h.admit(GOOD);h.admit(BAD);h.admit(GOOD)
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_BASELINE'): h.select(old.identity)
        c=h.select(old.identity,legacy=True);c.page()
        self.assertTrue(c.closed);self.assertEqual(c.public_after,0)
        self.assertEqual(c.emitted,[]);self.assertIsNone(c.gap)

    def test_injected_violation_before_checkpoint_cannot_certify_interval(self):
        h,log=self.house();h.admit(GOOD);c=h.select(log.identity);c.page()
        log.rows[0]=BAD;c.checkpoint()
        self.assertTrue(c.closed);self.assertEqual(c.checkpoints,[])

    def test_checkpoint_cannot_skip_unscanned_N(self):
        h,log=self.house();log.rows=[GOOD,BAD,GOOD];c=h.select(log.identity)
        with self.assertRaisesRegex(ValueError,'UNSCANNED_INTERVAL'): c.checkpoint()

if __name__=='__main__': unittest.main(verbosity=2)

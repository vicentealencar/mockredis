from unittest import TestCase
from mockredis import MockRedis


class TestRedisZset(TestCase):
    """zset tests"""

    def setUp(self):
        self.redis = MockRedis()
        self.redis.flushdb()

    def test_zadd(self):
        key = "zset"
        values = [("one", 1), ("uno", 1), ("two", 2), ("three", 3)]
        for member, score in values:
            self.assertEquals(1, self.redis.zadd(key, member, score))

    def test_zadd_strict(self):
        """Argument order for zadd depends on strictness"""
        self.redis.strict = True
        key = "zset"
        values = [("one", 1), ("uno", 1), ("two", 2), ("three", 3)]
        for member, score in values:
            self.assertEquals(1, self.redis.zadd(key, score, member))

    def test_zadd_duplicate_key(self):
        key = "zset"
        self.assertEquals(1, self.redis.zadd(key, "one", 1.0))
        self.assertEquals(0, self.redis.zadd(key, "one", 2.0))

    def test_zadd_wrong_type(self):
        key = "zset"
        self.redis.set(key, "value")
        with self.assertRaises(Exception):
            self.redis.zadd(key, "one", 2.0)

    def test_zadd_multiple_bad_args(self):
        key = "zset"
        args = ["one", 1, "two"]
        with self.assertRaises(Exception):
            self.redis.zadd(key, *args)

    def test_zadd_multiple_bad_score(self):
        key = "zset"
        with self.assertRaises(Exception):
            self.redis.zadd(key, "one", "two")

    def test_zadd_multiple_args(self):
        key = "zset"
        args = ["one", 1, "uno", 1, "two", 2, "three", 3]
        self.assertEquals(4, self.redis.zadd(key, *args))

    def test_zadd_multiple_kwargs(self):
        key = "zset"
        kwargs = {"one": 1, "uno": 1, "two": 2, "three": 3}
        self.assertEquals(4, self.redis.zadd(key, **kwargs))

    def test_zcard(self):
        key = "zset"
        self.assertEquals(0, self.redis.zcard(key))
        self.redis.zadd(key, "one", 1)
        self.assertEquals(1, self.redis.zcard(key))
        self.redis.zadd(key, "one", 2)
        self.assertEquals(1, self.redis.zcard(key))
        self.redis.zadd(key, "two", 2)
        self.assertEquals(2, self.redis.zcard(key))

    def test_zincrby(self):
        key = "zset"
        self.assertEquals(1.0, self.redis.zincrby(key, "member1"))
        self.assertEquals(2.0, self.redis.zincrby(key, "member2", 2))
        self.assertEquals(-1.0, self.redis.zincrby(key, "member1", -2))

    def test_zrange(self):
        key = "zset"
        self.assertEquals([], self.redis.zrange(key, 0, -1))
        self.redis.zadd(key, "one", 1.5)
        self.redis.zadd(key, "two", 2.5)
        self.redis.zadd(key, "three", 3.5)

        # full range
        self.assertEquals(["one", "two", "three"],
                          self.redis.zrange(key, 0, -1))
        # withscores
        self.assertEquals([("one", 1.5), ("two", 2.5), ("three", 3.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))
        # score_cast_func
        self.assertEquals([("one", 1), ("two", 2), ("three", 3)],
                          self.redis.zrange(key, 0, -1, withscores=True, score_cast_func=int))

        # positive ranges
        self.assertEquals(["one"], self.redis.zrange(key, 0, 0))
        self.assertEquals(["one", "two"], self.redis.zrange(key, 0, 1))
        self.assertEquals(["one", "two", "three"], self.redis.zrange(key, 0, 2))
        self.assertEquals(["one", "two", "three"], self.redis.zrange(key, 0, 3))
        self.assertEquals(["two", "three"], self.redis.zrange(key, 1, 2))
        self.assertEquals(["three"], self.redis.zrange(key, 2, 3))

        # negative ends
        self.assertEquals(["one", "two", "three"], self.redis.zrange(key, 0, -1))
        self.assertEquals(["one", "two"], self.redis.zrange(key, 0, -2))
        self.assertEquals(["one"], self.redis.zrange(key, 0, -3))
        self.assertEquals([], self.redis.zrange(key, 0, -4))

        # negative starts
        self.assertEquals([], self.redis.zrange(key, -1, 0))
        self.assertEquals(["three"], self.redis.zrange(key, -1, -1))
        self.assertEquals(["two", "three"], self.redis.zrange(key, -2, -1))
        self.assertEquals(["one", "two", "three"], self.redis.zrange(key, -3, -1))
        self.assertEquals(["one", "two", "three"], self.redis.zrange(key, -4, -1))

        # desc
        self.assertEquals(["three", "two", "one"], self.redis.zrange(key, 0, 2, desc=True))
        self.assertEquals(["two", "one"], self.redis.zrange(key, 1, 2, desc=True))
        self.assertEquals(["three", "two"], self.redis.zrange(key, 0, 1, desc=True))

    def test_zrem(self):
        key = "zset"
        self.assertFalse(self.redis.zrem(key, "two"))

        self.redis.zadd(key, "one", 1.0)
        self.assertEquals(1, self.redis.zcard(key))

        self.assertTrue(self.redis.zrem(key, "one"))
        self.assertEquals(0, self.redis.zcard(key))

    def test_zscore(self):
        key = "zset"
        self.assertEquals(None, self.redis.zscore(key, "one"))

        self.redis.zadd(key, "one", 1.0)
        self.assertEquals(1.0, self.redis.zscore(key, "one"))

    def test_zrank(self):
        key = "zset"
        self.assertEquals(None, self.redis.zrank(key, "two"))

        self.redis.zadd(key, "one", 1.0)
        self.redis.zadd(key, "two", 2.0)
        self.assertEquals(0, self.redis.zrank(key, "one"))
        self.assertEquals(1, self.redis.zrank(key, "two"))

    def test_zcount(self):
        key = "zset"
        self.assertEquals(0, self.redis.zcount(key, "-inf", "inf"))

        self.redis.zadd(key, "one", 1.0)
        self.redis.zadd(key, "two", 2.0)

        self.assertEquals(2, self.redis.zcount(key, "-inf", "inf"))
        self.assertEquals(1, self.redis.zcount(key, "-inf", 1.0))
        self.assertEquals(1, self.redis.zcount(key, "-inf", 1.5))
        self.assertEquals(2, self.redis.zcount(key, "-inf", 2.0))
        self.assertEquals(2, self.redis.zcount(key, "-inf", 2.5))
        self.assertEquals(1, self.redis.zcount(key, 0.5, 1.0))
        self.assertEquals(1, self.redis.zcount(key, 0.5, 1.5))
        self.assertEquals(2, self.redis.zcount(key, 0.5, 2.0))
        self.assertEquals(2, self.redis.zcount(key, 0.5, 2.5))
        self.assertEquals(2, self.redis.zcount(key, 0.5, "inf"))

        self.assertEquals(0, self.redis.zcount(key, "inf", "-inf"))
        self.assertEquals(0, self.redis.zcount(key, 2.0, 0.5))

    def test_zrangebyscore(self):
        key = "zset"
        self.assertEquals([], self.redis.zrangebyscore(key, "-inf", "inf"))
        self.redis.zadd(key, "one", 1.5)
        self.redis.zadd(key, "two", 2.5)
        self.redis.zadd(key, "three", 3.5)

        self.assertEquals(["one", "two", "three"],
                          self.redis.zrangebyscore(key, "-inf", "inf"))
        self.assertEquals([("one", 1.5), ("two", 2.5), ("three", 3.5)],
                          self.redis.zrangebyscore(key, "-inf", "inf", withscores=True))
        self.assertEquals([("one", 1), ("two", 2), ("three", 3)],
                          self.redis.zrangebyscore(key,
                                                   "-inf",
                                                   "inf",
                                                   withscores=True,
                                                   score_cast_func=int))

        self.assertEquals(["one"],
                          self.redis.zrangebyscore(key, 1.0, 2.0))
        self.assertEquals(["one", "two"],
                          self.redis.zrangebyscore(key, 1.0, 3.0))
        self.assertEquals(["one"],
                          self.redis.zrangebyscore(key, 1.0, 3.0, start=0, num=1))
        self.assertEquals(["two"],
                          self.redis.zrangebyscore(key, 1.0, 3.0, start=1, num=1))
        self.assertEquals(["two", "three"],
                          self.redis.zrangebyscore(key, 1.0, 3.5, start=1, num=4))
        self.assertEquals([],
                          self.redis.zrangebyscore(key, 1.0, 3.5, start=3, num=4))

    def test_zremrank(self):
        key = "zset"
        self.assertEquals(None, self.redis.zrevrank(key, "two"))

        self.redis.zadd(key, "one", 1.0)
        self.redis.zadd(key, "two", 2.0)
        self.assertEquals(1, self.redis.zrevrank(key, "one"))
        self.assertEquals(0, self.redis.zrevrank(key, "two"))

    def test_zrevrangebyscore(self):
        key = "zset"
        self.assertEquals([], self.redis.zrevrangebyscore(key, "inf", "-inf"))
        self.redis.zadd(key, "one", 1.5)
        self.redis.zadd(key, "two", 2.5)
        self.redis.zadd(key, "three", 3.5)

        self.assertEquals(["three", "two", "one"],
                          self.redis.zrevrangebyscore(key, "inf", "-inf"))
        self.assertEquals([("three", 3.5), ("two", 2.5), ("one", 1.5)],
                          self.redis.zrevrangebyscore(key, "inf", "-inf", withscores=True))
        self.assertEquals([("three", 3), ("two", 2), ("one", 1)],
                          self.redis.zrevrangebyscore(key,
                                                      "inf",
                                                      "-inf",
                                                      withscores=True,
                                                      score_cast_func=int))

        self.assertEquals(["one"],
                          self.redis.zrevrangebyscore(key, 2.0, 1.0))
        self.assertEquals(["two", "one"],
                          self.redis.zrevrangebyscore(key, 3.0, 1.0))
        self.assertEquals(["two"],
                          self.redis.zrevrangebyscore(key, 3.0, 1.0, start=0, num=1))
        self.assertEquals(["one"],
                          self.redis.zrevrangebyscore(key, 3.0, 1.0, start=1, num=1))
        self.assertEquals(["two", "one"],
                          self.redis.zrevrangebyscore(key, 3.5, 1.0, start=1, num=4))
        self.assertEquals([],
                          self.redis.zrevrangebyscore(key, 3.5, 1.0, start=3, num=4))

    def test_zremrangebyrank(self):
        key = "zset"
        self.assertEquals(0, self.redis.zremrangebyrank(key, 0, -1))

        self.redis.zadd(key, "one", 1.0)
        self.redis.zadd(key, "two", 2.0)
        self.redis.zadd(key, "three", 3.0)

        self.assertEquals(2, self.redis.zremrangebyrank(key, 0, 1))

        self.assertEquals(["three"], self.redis.zrange(key, 0, -1))
        self.assertEquals(1, self.redis.zremrangebyrank(key, 0, -1))

        self.assertEquals([], self.redis.zrange(key, 0, -1))

    def test_zremrangebyscore(self):
        key = "zset"
        self.assertEquals(0, self.redis.zremrangebyscore(key, "-inf", "inf"))

        self.redis.zadd(key, "one", 1.0)
        self.redis.zadd(key, "two", 2.0)
        self.redis.zadd(key, "three", 3.0)

        self.assertEquals(1, self.redis.zremrangebyscore(key, 0, 1))

        self.assertEquals(["two", "three"], self.redis.zrange(key, 0, -1))
        self.assertEquals(2, self.redis.zremrangebyscore(key, 2.0, "inf"))

        self.assertEquals([], self.redis.zrange(key, 0, -1))

    def test_zunionstore_no_keys(self):
        key = "zset"

        self.assertEquals(0, self.redis.zunionstore(key, ["zset1", "zset2"]))

    def test_zunionstore_default(self):
        # sum is default
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"]))
        self.assertEquals([("one", 1.0), ("three", 3.0), ("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_sum(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="sum"))
        self.assertEquals([("one", 1.0), ("three", 3.0), ("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_SUM(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="SUM"))
        self.assertEquals([("one", 1.0), ("three", 3.0), ("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_min(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="min"))
        self.assertEquals([("one", 1.0), ("two", 2.0), ("three", 3.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_MIN(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="MIN"))
        self.assertEquals([("one", 1.0), ("two", 2.0), ("three", 3.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_max(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        key = "zset"
        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="max"))
        self.assertEquals([("one", 1.0), ("two", 2.5), ("three", 3.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zunionstore_MAX(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        key = "zset"
        self.assertEquals(3, self.redis.zunionstore(key, ["zset1", "zset2"], aggregate="MAX"))
        self.assertEquals([("one", 1.0), ("two", 2.5), ("three", 3.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_no_keys(self):
        key = "zset"

        # no keys
        self.assertEquals(0, self.redis.zinterstore(key, ["zset1", "zset2"]))

    def test_zinterstore_default(self):
        # sum is default
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"]))
        self.assertEquals([("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_sum(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="sum"))
        self.assertEquals([("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_SUM(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="SUM"))
        self.assertEquals([("two", 4.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_min(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="min"))
        self.assertEquals([("two", 2.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_MIN(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="MIN"))
        self.assertEquals([("two", 2.0)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_max(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="max"))
        self.assertEquals([("two", 2.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

    def test_zinterstore_MAX(self):
        key = "zset"
        self.redis.zadd("zset1", "one", 1.0)
        self.redis.zadd("zset1", "two", 2.0)
        self.redis.zadd("zset2", "two", 2.5)
        self.redis.zadd("zset2", "three", 3.0)

        self.assertEquals(1, self.redis.zinterstore(key, ["zset1", "zset2"], aggregate="MAX"))
        self.assertEquals([("two", 2.5)],
                          self.redis.zrange(key, 0, -1, withscores=True))

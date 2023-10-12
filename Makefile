.PHONY: clean test

test: Sched.py test.in
	env python3 Sched.py test.in > out.txt

clean:
	-rm out.txt

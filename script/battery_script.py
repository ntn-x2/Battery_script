import subprocess, time, re, sys, signal, getopt, os
from sched import scheduler
from threading import Thread

alert_shown = False
charging_checker_started = False

status_rate = 8
charge_rate = 4
battery_level = 28

class BatteryPowerChecker(Thread):
	def __init__(self, interval_rate):
		Thread.__init__(self)
		self.daemon = True
		self._interval_rate = interval_rate


	def run(self):
		global alert_shown
		#first_round_passed = False
		#print "Battery power checker started"

		while True:
			#if first_round_passed:
				#print "Other round of battery power checker"
			charging_status_command = "pmset -g batt"
			result = subprocess.Popen(charging_status_command, stdout = subprocess.PIPE, shell = True).stdout.read()
			status = re.search(r"(dis)?charg(.*);", result)
			status = status.group(0)[:-1] if status is not None else ""		#We discard the event in which status is "AC attached"
			#Possible statuses are "charging", "charged", "discharging" and "AC attached"
			#print "Battery status : %s\n" % status
			#print "Alert_shown : %s" % alert_shown
			#print "Chargin_checker_started: %s" % charging_checker_started
			if status == "discharging" and not alert_shown and not charging_checker_started:
				self.change_charging_status_checker(start = True)
			elif status != "discharging" and charging_checker_started:
				self.change_charging_status_checker(start = False)
			elif status == "charging" and alert_shown:
				alert_shown = False
			time.sleep(self._interval_rate)
			#first_round_passed = True

	def change_charging_status_checker(self, start):
		global charging_checker_started
		if start:
			#print "Starting battery charge checker...\n"
			#start the other thread
			self._charging_checker_thread = BatteryChargeChecker()
			self._charging_checker_thread.start()
			charging_checker_started = True
		else:
			#print "Stopping battery charge checker...\n"
			#stop the other thread
			self._charging_checker_thread.stop()
			self._charging_checker_thread = None
			charging_checker_started = False

class BatteryChargeChecker(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.daemon = True
		self._should_stop = False

	def run(self):
		global alert_shown
		#print "Battery charge checker started"
		#first_round_passed = False
		while not self._should_stop:
			#if first_round_passed:
				#print "Other round of battery charge checker" 
			battery_command = "ioreg -l | awk '$3~/Capacity/{c[$3]=$5}END{OFMT=\"%.3f\";max=c[\"\\\"MaxCapacity\\\"\"];print(max>0?100*c[\"\\\"CurrentCapacity\\\"\"]/max:\"?\")}'"
			subp = subprocess.Popen(battery_command, stdout = subprocess.PIPE, shell = True)
			battery_percentage = float(subp.stdout.read())
			#print "Battery percentage : %.2f\n" % battery_percentage

			if not alert_shown and battery_percentage <= battery_level:
				show_alert()
				self.stop()
			if not self._should_stop:		#It stoppes instantly if the other thread puts the boolean to false
				time.sleep(charge_rate)
			#first_round_passed = True
		else:
			print "Battery charge checker stopped\n"
			global charging_checker_started
			charging_checker_started = False
			self = None

	def stop(self):
		print "Battery charge checker stopping"
		self._should_stop = True

def show_alert():
	global alert_shown
	popup_title = "BATTERY LEVEL LOW!"
	popup_message = "PLUG CHARGE AS SOON AS YOU ARE WONDERFUL"
	alert_command = "osascript -e 'tell app \"System Events\" to display dialog \"%s\" buttons {\"OK\"} with title \"%s\" with icon caution'" % (popup_message, popup_title)
	sound_command = "say -v Whisper battery out!"
	#TODO: ADD SOUND TO THE DIALOG
	subprocess.Popen(alert_command, shell = True)
	subprocess.Popen(sound_command, shell = True)
	alert_shown = True

def stop_script(signal, frame):
	try:
		print "\nGoodbye!"
		sys.exit(0)
	except Exception:
		pass

def main():
	global status_rate
	global charge_rate
	global battery_level

	signal.signal(signal.SIGINT, stop_script)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:c:b:")
		stat_rate = [args[1] for args in opts if args[0] == "-c"]
		batt_rate = [args[1] for args in opts if args[0] == "-s"]
		batt_level = [args[1] for args in opts if args[0] == "-b"]
		help = [args[1] for args in opts if args[0] == "-h"]
		if len(help) > 0:
			print "Allowed parameters: -c battery status interval rate (integer, default = 60 s), -s battery level interval rate (integer, default = 20s, -b battery level treshold (integer, default = 20%)"
		else:
			error = False
			if len(stat_rate) > 0:
				try:
					status_rate = int(stat_rate[0])
				except ValueError:
					error = True
					print "Value must be an integer."
			if len(batt_rate) > 0:
				try:
					charge_rate = int(batt_rate[0])
				except ValueError:
					error = True
					print "Value must be an integer."
			if len(batt_level) > 0:
				try:
					battery_level = int(batt_level[0])
				except ValueError:
					error = True
					print "Value must be an integer."

			if not error:
				BatteryPowerChecker(status_rate).start()
				while True:
					time.sleep(1)				#Used to keep main thread alive
	except getopt.GetoptError:
		print "Allowed parameters: -c battery status interval rate (integer, default = 60 s), -s battery level interval rate (integer, default = 20s, -b battery level treshold (integer, default = 20%)"

if __name__ == "__main__":
	main()

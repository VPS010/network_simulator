class CRC:
    def _init_(self):
        self.input = ""
        self.divisor = ""
        self.divident = ""
        self.result = ""
        self.len_divident = 0
        self.len_gen = 0
        self.len_inp = 0

    def fun_xor(self, a, b):
        result = ""
        if a[0] == '0':
            return a[1:]
        else:
            for i in range(self.len_gen):
                result += '0' if a[i] == b[i] else '1'
            return result[1:]

    def modulo_div(self):
        temp_div = self.divisor
        temp_divident = self.divident[:self.len_gen]
        j = self.len_gen
        while j < self.len_divident:
            temp_divident = self.fun_xor(temp_divident, temp_div)
            temp_divident += self.divident[j]
            j += 1
        self.result = self.input + self.fun_xor(temp_divident, self.divisor)

    def getdata(self):
        self.input = input("Enter Source Input: ")
        self.divisor = input("Enter Coefficients of generator polynomial: ")
        self.len_gen = len(self.divisor)
        self.len_inp = len(self.input)
        self.divident = self.input
        r = self.len_gen - 1
        for i in range(r):
            self.divident += '0'
        self.len_divident = len(self.divident)
        self.modulo_div()

    def sender_side(self):
        print("Input:", self.input)
        print("Polynomial:", self.divisor)
        print("Divident:", self.divident)
        print("Data to send:", self.result)

    def receiver_side(self):
        data_rec = input("Enter Data Received: ")
        temp_div = self.divisor
        temp_divident = data_rec[:self.len_gen]
        j = self.len_gen
        while j < len(data_rec):
            temp_divident = self.fun_xor(temp_divident, temp_div)
            temp_divident += data_rec[j]
            j += 1
        error = self.fun_xor(temp_divident, self.divisor)
        print("Remainder is:", error)
        flag = False
        for i in range(self.len_gen - 1):
            if error[i] == '1':
                flag = True
                break
        if not flag:
            print("Correct Data Received Without Any Error")
        else:
            print("Data Received Contains Some Error")

crc = CRC()
crc.getdata()
crc.sender_side()
crc.receiver_side()
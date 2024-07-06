#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 高效Python装饰器decorator
# 功能描述：Python 封装器是添加到另一个函数中的函数，然后可以添加额外的功能或修改其行为，
# 而不直接改变其源代码。它们通常以装饰器的形式实现，这是一种特殊的函数，将另一个函数作为
# 输入，并对其功能进行一些修改。
#
# -----------------------
# 封装器函数在各种情况下都很有用：
# I. 功能扩展（Functionality Extension）：可以通过用装饰器包装我们的函数来增加诸如日志、性
# II. 能测量或缓存等功能。
# III. 代码可重用性：可以将一个封装函数甚至一个类应用于多个实体，从而避免代码的重复，并确保不同
# 组件的行为一致。
# IV. 行为修改：我们可以拦截输入参数，例如，验证输入变量，而不需要许多assert行。
# -----------------------
# 1. 计时器包装器
# 2. 调试器封装器
# 3. 异常处理程序包装器
# 4. 输入验证器包装器
# 5. 函数重试封装器
#
# -----------------------
#
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------


# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------

# import logging

import time

# --------------------------------------------------------------------
# ***
# 日志和参数配置
# ***
# --------------------------------------------------------------------

# *** ---------- 日志 ----------
# logger
# logger = logging.getLogger()


# --------------------------------------------------------------------
# ***
# 计时器包装器 Timer
# ***
# 这个封装器函数测量一个函数的执行时间，并打印出已用的时间。
# 它对于剖析和优化代码非常有用。
# --------------------------------------------------------------------

def timer(func):
    def wrapper(*args, **kwargs):
        # start the timer
        start_time = time.time()
        # call the decorated function
        result = func(*args, **kwargs)
        # remeasure the time
        end_time = time.time()
        # compute the elapsed time and print it
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        # return the result of the decorated function execution
        return result
    
    # return reference to the wrapper function
    return wrapper


@timer
def train_model():
    print("Starting the model training function...")
    
    # simulate a function execution by pausing the program for 5 seconds
    time.sleep(5)

    print("Model training completed!")

train_model()




# --------------------------------------------------------------------
# ***
# 调试器封装器 Debugger
# ***
# 可以创建一个额外的有用的包装函数，通过打印每个函数的输入和输出来促进调试。
# 这种方法能够深入了解各种函数的执行流程，而不必用多个打印语句来干扰应用程序逻辑。
# --------------------------------------------------------------------

def debug(func):
    def wrapper(*args, **kwargs):
        # print the fucntion name and arguments
        print(f"Calling {func.__name__} with args: {args} kwargs: {kwargs}")
        # call the function
        result = func(*args, **kwargs)
        # print the results
        print(f"{func.__name__} returned: {result}")
        return result
    
    return wrapper


@debug
def add_numbers(x, y):
    return x + y

add_numbers(7, y=5,)  
# Output: Calling add_numbers with args: (7) kwargs: {'y': 5} \n add_numbers returned: 12



# --------------------------------------------------------------------
# ***
# 异常处理程序包装器 exception_handler
# ***
# 封装器的 exception_handler 将捕获在 divide 函数中引发的任何异常，并对其进行相应处理。
# 以根据你的要求定制包装函数中的异常处理方式，例如记录异常或执行额外的错误处理步骤。
# --------------------------------------------------------------------

def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Handle the exception
            print(f"An exception occurred: {str(e)}")
            # Optionally, perform additional error handling or logging
            # Reraise the exception if needed
    
    return wrapper


@exception_handler
def divide(x, y):
    result = x / y
    return result

divide(10, 0)  
# Output: An exception occurred: division by zero



# --------------------------------------------------------------------
# ***
# 输入验证器包装器 Input Validator
# ***
# 这个封装函数根据指定的条件或数据类型验证一个函数的输入参数。
# 它可以用来确保输入数据的正确性和一致性。
# 另一种方法是在我们想要验证输入数据的函数内创建无数的assert行，来实现这一目的。
# --------------------------------------------------------------------

def validate_input(*validations):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i, val in enumerate(args):
                if i < len(validations):
                    if not validations[i](val):
                        raise ValueError(f"Invalid argument: {val}")
            for key, val in kwargs.items():
                if key in validations[len(args):]:
                    if not validations[len(args):][key](val):
                        raise ValueError(f"Invalid argument: {key}={val}")
            return func(*args, **kwargs)
        return wrapper
    
    return decorator


# 为了调用验证的输入，我们需要定义验证函数。例如，可以使用两个验证函数。
# 第一个函数（lambda x: x > 0）检查参数x是否大于0，
# 第二个函数（lambda y: isinstance(y, str)）检查参数y是否属于字符串类型。
@validate_input(lambda x: x > 0, lambda y: isinstance(y, str))
def divide_and_print(x, message):
    print(message)
    
    return 1 / x

divide_and_print(5, "Hello!")  # Output: Hello! 1.0



# --------------------------------------------------------------------
# ***
# 函数重试封装器 Retry
# ***
# 这个封装器会重试一个函数的执行，并在重试之间有一定的延迟。
# 在处理网络或API调用时，它可能会因为临时问题而偶尔失败，因此很有用。
# 另一种方法是在我们想要验证输入数据的函数内创建无数的assert行，来实现这一目的。
# --------------------------------------------------------------------

def retry(max_attempts, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    time.sleep(delay)
            print(f"Function failed after {max_attempts} attempts")
        return wrapper
    
    return decorator


@retry(max_attempts=3, delay=2)
def fetch_data(url):
    print("Fetching the data..")
    # raise timeout error to simulate a server not responding..
    raise TimeoutError("Server is not responding.")

fetch_data("https://example.com/data")  
# Retries 3 times with a 2-second delay between attempts



import datetime
import os
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

#==============================================#
    # In this file (in-order as they appear):
    #       BatchSimulation(ABCMeta)
    #       SimulationResult @dataclass
    #       BatchSimFileWriter
#==============================================#

#==============================================#
# START CLASSES
#==============================================#

class BatchSimulation(metaclass=ABCMeta):
    '''
    Serves as an abstract base class for running a batch-simulation of a market strategy.

    Notes:

    If using multiprocessing or clustering to execute multiple batch processes at once,
    make sure there is one object per batch test!

    The `execute` method accepts a **kwargs much like the `prepare` method does.
    This was done so that implementations of `BatchSimulation` can instead send the params
    through the `execute` method instead of `prepare` if desired.
    Of course, it would also be a good idea to still implement a `prepare` method, but when
    `execute` is called, internally call `prepare`, passing along the **kwargs. This gives users
    the freedom to either call directly to the `exectute` method, but also be able to take
    advantage of the ability to set the parameters and call on `execute` later on.

    Usage pattern example:

        sim = MySimulation(ohlc_data=data, name='My_Sim')
        # Arbitrary kwargs in the prepare:
        sim.prepare(start_delta=10, end_delta=20)
        sim.execute()

        print(sim.results)

        sim.prepare(...)
        sim.execute()

        #....
    '''
    def __init__(self, ohlc_data, name, description='', on_finish_callback=None):
        '''
        ohlc_data: `list[OhlcData]` list of the data to run the simulation over.

        name: `str` A name for this batch test. Important if writing to file!

        description: `str` a short description of the batch test and the scenarios under test.
        Note that some implementations might override and offer a custom description with
        interpolated parameter values to easily output test scenarios.

        on_finish_callback: `def(BatchSimulation)` method that, if not none,
        will be called on completion. Expects one parameter of BatchSimulation.
        '''
        self._data =ohlc_data
        self._name = name
        self._description = description
        self._callback = on_finish_callback
        self._results = []

    def execute(self, **kwargs):
        '''
        Execute the batch simulation. Will overwrite any previous results.

        Allows for  an additional kwargs passing for any setup.
        '''

        self._results = []

        self._simulate(**kwargs)

        if self._callback is not None:
            self._callback(self)

    def _report_result(self, sim_result):
        '''
        Used internally to track the result of a batch-test scenario.

        If testing every moving average from 5-200, at the end of each iteration,
        you would create a `SimulationResult` object with the result data, and pass
        it along to here to be logged.
        '''
        self._results.append(sim_result)

    def prepare(self, **kwargs):
        '''
        Set the variables for a simulation here before running.

        Subclasses can override this method on a case-by-case basis.

        For optimal workflow, it is reccomended to call on this within `_simulate()`
        with the kwargs (if any) passed through for flexibility.
        '''

    @abstractmethod
    def _simulate(self, **kwargs):
        '''
        **kwargs: additional optional parameters to pass through to the method.

        Abstract method where the batch simulation takes place.
        In implementing classes, all of the batch scenarios are handled here,
        likely through a series of loops. It is up to implementing classes
        to supply more parameters as needed for knowing what variables to test.
        '''

    def setmeta(self, name=None, description=None):
        '''Update the meta name and description of a test.

        If an optional argument is not supplied, or is None,
        it will remain its previous value.'''
        if name is not None:
            self._name = name
        if description is not None:
            self._description = description

    def results_sorted(self, descending=True):
        '''
        Returns the results in sorted order.

        `descending` default true: should the `value` be sorted in descending order?
        '''
        return sorted(self._results, key=lambda x: x.value, reverse=descending)

    @property
    def results(self):
        '''Return the list of `SimulationResult`s.'''
        return self._results

    @property
    def name(self):
        '''Return the name of this test case.'''
        return self._name

    @property
    def description(self):
        '''Return the description of this batch test.'''
        return self._description

@dataclass
class SimulationResult:
    '''
    Value:Description pair object for a simulation result.
    '''
    value: float
    descriptor: str

    def __init__(self, value, descriptor):
        '''
        value: `float` the quantifiable value marking the performance of a given sim result.
        Typically, it's the percent gain of the algorithm.

        descriptor: `str` A string typically denoting the parameters used in the result.
        '''
        self.value = value
        self.descriptor = descriptor

class BatchSimFileWriter:
    '''
    Use as a default output source to write the results of a `BatchSimulation` to a text file.

    Utilizes the name property of a batch simulation for the filename, along with an iso timestamp
    if unique names are desired.
    '''
    def __init__(self, target_dir, write_unique=True, file_type='.txt', show_results=0, sorted_results=True, desc=True):
        '''
        target_dir: `str` the path to the target directory. Absolute paths are preferred.

        write_unique: `bool` if true, will append a timestamp to the end of an output file.
        This helps in the case of not wanting to overwrite any previous results.

        file_type: `str` default .txt. the type of file to write the output to.

        show_results: `int` the number of results to show in the output file. If 0, write all data to file. Recommended to pair with `sorted_results` and `desc`.

        sorted_results: `bool` if true, the output file will sort the results by SimulationResult value.

        desc: `bool` if true, the sorted results will be shown in descending order. Only valid
        if sorted_results is true.
        '''
        self._target = target_dir
        self._unique = write_unique
        self._file_type = file_type
        self._show_results = show_results
        self._sort_results = sorted_results
        self._descending_results = desc

        self._header_width = 70
        self._decimals = 2

    def on_batch_finish(self, batch_simulation):
        '''
        Direct corresponding method to the callback in the batch simulation constructor.
        '''
        fpath = os.path.join(self._target, batch_simulation.name)

        if self._unique:
            fpath += datetime.datetime.utcnow().isoformat()

        fpath += self._file_type

        with open(fpath, 'w') as output:
            #  Write out the test name, description, an area for notes
            output.write(batch_simulation.name)
            output.write('\n\n')
            output.write(batch_simulation.description)
            output.write('\n\n')

            output.write(('*'*self._header_width) +'\n')
            output.write('Notes:\n\n')
            output.write(('*'*self._header_width) +'\n\n')

            # Results:
            output.write('Result:\t\tData:\n')
            data = []
            if self._sort_results:
                data = batch_simulation.results_sorted(self._descending_results)
            else:
                data = batch_simulation.results

            toShow = self._show_results
            if toShow == 0 or toShow > len(data):
                toShow = len(data)

            for result in range(0, toShow):
                out = str(round(data[result].value,self._decimals)) + '\t\t' + data[result].descriptor
                output.write(out + '\n')
            